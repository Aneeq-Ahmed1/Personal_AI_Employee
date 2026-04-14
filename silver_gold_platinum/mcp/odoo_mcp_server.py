"""
Odoo MCP Server - Gold Tier
Provides integration with Odoo 19 for accounting, invoices, sales, and inventory.
"""

from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import requests
import logging
from datetime import datetime
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('odoo_mcp_server')

app = Flask(__name__)

# Odoo Configuration
ODOO_CONFIG = {
    'url': os.getenv('ODOO_URL', 'http://localhost:8069'),
    'db': os.getenv('ODOO_DB', 'odoo'),
    'username': os.getenv('ODOO_USERNAME', 'admin'),
    'password': os.getenv('ODOO_PASSWORD', 'admin'),
    'api_key': os.getenv('ODOO_API_KEY', ''),
}


def odoo_rpc_call(model, method, args=None, kwargs=None):
    """
    Make an RPC call to Odoo server.
    
    Args:
        model: Odoo model name (e.g., 'account.move', 'sale.order')
        method: Method to call (e.g., 'search_read', 'create')
        args: Positional arguments
        kwargs: Keyword arguments
    
    Returns:
        dict: RPC response or error
    """
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    
    url = f"{ODOO_CONFIG['url']}/jsonrpc"
    
    # Prepare authentication
    if ODOO_CONFIG['api_key']:
        # API Key authentication (Odoo 15+)
        auth = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'service': 'common',
                'method': 'authenticate',
                'args': [
                    ODOO_CONFIG['db'],
                    ODOO_CONFIG['username'],
                    ODOO_CONFIG['password'],
                    {'api_key': ODOO_CONFIG['api_key']}
                ]
            },
            'id': 1
        }
    else:
        # Password authentication
        auth = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'service': 'common',
                'method': 'login',
                'args': [
                    ODOO_CONFIG['db'],
                    ODOO_CONFIG['username'],
                    ODOO_CONFIG['password']
                ]
            },
            'id': 1
        }
    
    try:
        # Get UID
        response = requests.post(url, json=auth, timeout=10)
        response.raise_for_status()
        uid = response.json().get('result')
        
        if not uid:
            logger.error("Odoo authentication failed")
            return {'success': False, 'error': 'Authentication failed'}
        
        # Make RPC call
        rpc_payload = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'service': 'object',
                'method': 'execute_kw',
                'args': [
                    ODOO_CONFIG['db'],
                    uid,
                    ODOO_CONFIG['password'],
                    model,
                    method,
                    args,
                    kwargs
                ]
            },
            'id': 2
        }
        
        response = requests.post(url, json=rpc_payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if 'error' in result:
            logger.error(f"Odoo RPC error: {result['error']}")
            return {'success': False, 'error': result['error'].get('message', 'Unknown error')}
        
        return {'success': True, 'result': result.get('result')}
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Odoo connection error: {str(e)}")
        return {'success': False, 'error': f'Connection error: {str(e)}'}
    except Exception as e:
        logger.error(f"Odoo RPC call failed: {str(e)}")
        return {'success': False, 'error': str(e)}


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Odoo MCP Server',
        'version': '1.0.0',
        'endpoints': [
            '/account/invoices',
            '/account/journal-items',
            '/sales/orders',
            '/sales/quotation',
            '/partners',
            '/products',
            '/test-connection'
        ]
    })


@app.route('/test-connection', methods=['GET'])
def test_connection():
    """Test Odoo connection"""
    result = odoo_rpc_call('res.partner', 'search_read', [[]], {
        'limit': 1,
        'fields': ['id', 'name', 'email']
    })

    if result.get('success'):
        return jsonify({
            'status': 'connected',
            'odoo_url': ODOO_CONFIG['url'],
            'database': ODOO_CONFIG['db'],
            'message': 'Successfully connected to Odoo'
        })
    else:
        return jsonify({
            'status': 'disconnected',
            'error': result.get('error', 'Unknown error')
        }), 500


@app.route('/account/invoices', methods=['GET'])
def get_invoices():
    """
    Get account invoices.
    
    Query params:
        - state: Filter by state (draft, posted, cancel)
        - move_type: Filter by type (out_invoice, in_invoice, out_refund, in_refund)
        - partner_id: Filter by partner
        - limit: Max results (default: 100)
    """
    try:
        domain = []
        
        # Apply filters
        if state := request.args.get('state'):
            domain.append(('state', '=', state))
        
        if move_type := request.args.get('move_type'):
            domain.append(('move_type', '=', move_type))
        
        if partner_id := request.args.get('partner_id'):
            domain.append(('partner_id', '=', int(partner_id)))
        
        limit = int(request.args.get('limit', 100))
        
        result = odoo_rpc_call('account.move', 'search_read', [domain], {
            'fields': ['name', 'partner_id', 'invoice_date', 'amount_total', 
                      'amount_residual', 'state', 'move_type', 'currency_id'],
            'order': 'invoice_date desc',
            'limit': limit
        })
        
        if result.get('success'):
            invoices = result.get('result', [])
            # Format partner_id and currency_id (they come as tuples)
            for invoice in invoices:
                if isinstance(invoice.get('partner_id'), tuple):
                    invoice['partner_name'] = invoice['partner_id'][1]
                    invoice['partner_id'] = invoice['partner_id'][0]
                if isinstance(invoice.get('currency_id'), tuple):
                    invoice['currency_name'] = invoice['currency_id'][1]
                    invoice['currency_id'] = invoice['currency_id'][0]
            
            return jsonify({
                'success': True,
                'count': len(invoices),
                'invoices': invoices
            })
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error getting invoices: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/account/invoices', methods=['POST'])
def create_invoice():
    """
    Create a new invoice.
    
    JSON body:
        - partner_id: Customer/Vendor ID (required)
        - move_type: 'out_invoice' or 'in_invoice' (default: out_invoice)
        - invoice_line_ids: List of invoice lines
            - product_id: Product ID
            - name: Description
            - quantity: Quantity (default: 1)
            - price_unit: Unit price
            - account_id: Account ID (optional)
    """
    try:
        data = request.get_json()
        
        partner_id = data.get('partner_id')
        if not partner_id:
            return jsonify({'success': False, 'error': 'partner_id is required'}), 400
        
        move_type = data.get('move_type', 'out_invoice')
        invoice_lines = data.get('invoice_line_ids', [])
        
        # Format invoice lines for Odoo
        lines_data = []
        for line in invoice_lines:
            lines_data.append((0, 0, {
                'product_id': line.get('product_id'),
                'name': line.get('name', ''),
                'quantity': line.get('quantity', 1),
                'price_unit': line.get('price_unit', 0),
                'account_id': line.get('account_id')
            }))
        
        invoice_data = {
            'partner_id': partner_id,
            'move_type': move_type,
            'invoice_line_ids': lines_data,
            'invoice_date': data.get('invoice_date', datetime.now().strftime('%Y-%m-%d')),
        }
        
        result = odoo_rpc_call('account.move', 'create', [invoice_data])
        
        if result.get('success'):
            invoice_id = result.get('result')
            return jsonify({
                'success': True,
                'invoice_id': invoice_id,
                'message': f'Invoice created successfully'
            })
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error creating invoice: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/account/invoices/<int:invoice_id>/post', methods=['POST'])
def post_invoice(invoice_id):
    """Post an invoice (validate it)"""
    try:
        result = odoo_rpc_call('account.move', 'action_post', [[invoice_id]])
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': f'Invoice {invoice_id} posted successfully'
            })
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error posting invoice: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/account/journal-items', methods=['GET'])
def get_journal_items():
    """
    Get account journal items (account move lines).
    
    Query params:
        - date_from: Filter from date
        - date_to: Filter to date
        - account_id: Filter by account
        - partner_id: Filter by partner
        - limit: Max results (default: 100)
    """
    try:
        domain = []
        
        if date_from := request.args.get('date_from'):
            domain.append(('date', '>=', date_from))
        
        if date_to := request.args.get('date_to'):
            domain.append(('date', '<=', date_to))
        
        if account_id := request.args.get('account_id'):
            domain.append(('account_id', '=', int(account_id)))
        
        if partner_id := request.args.get('partner_id'):
            domain.append(('partner_id', '=', int(partner_id)))
        
        limit = int(request.args.get('limit', 100))
        
        result = odoo_rpc_call('account.move.line', 'search_read', [domain], {
            'fields': ['date', 'name', 'account_id', 'partner_id', 
                      'debit', 'credit', 'balance', 'move_id'],
            'order': 'date desc',
            'limit': limit
        })
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'count': len(result.get('result', [])),
                'journal_items': result.get('result', [])
            })
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error getting journal items: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/sales/orders', methods=['GET'])
def get_sales_orders():
    """
    Get sales orders.
    
    Query params:
        - state: Filter by state (draft, sent, sale, done, cancel)
        - partner_id: Filter by customer
        - date_from: Filter from date
        - limit: Max results (default: 100)
    """
    try:
        domain = []
        
        if state := request.args.get('state'):
            domain.append(('state', '=', state))
        
        if partner_id := request.args.get('partner_id'):
            domain.append(('partner_id', '=', int(partner_id)))
        
        if date_from := request.args.get('date_from'):
            domain.append(('date_order', '>=', date_from))
        
        limit = int(request.args.get('limit', 100))
        
        result = odoo_rpc_call('sale.order', 'search_read', [domain], {
            'fields': ['name', 'partner_id', 'date_order', 'amount_total',
                      'amount_untaxed', 'state', 'user_id'],
            'order': 'date_order desc',
            'limit': limit
        })
        
        if result.get('success'):
            orders = result.get('result', [])
            # Format partner_id
            for order in orders:
                if isinstance(order.get('partner_id'), tuple):
                    order['partner_name'] = order['partner_id'][1]
                    order['partner_id'] = order['partner_id'][0]
            
            return jsonify({
                'success': True,
                'count': len(orders),
                'orders': orders
            })
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error getting sales orders: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/sales/orders', methods=['POST'])
def create_sales_order():
    """
    Create a new sales order.
    
    JSON body:
        - partner_id: Customer ID (required)
        - order_line: List of order lines
            - product_id: Product ID (required)
            - product_uom_qty: Quantity (default: 1)
            - price_unit: Unit price (optional)
        - date_order: Order date (optional, default: now)
    """
    try:
        data = request.get_json()
        
        partner_id = data.get('partner_id')
        if not partner_id:
            return jsonify({'success': False, 'error': 'partner_id is required'}), 400
        
        order_lines = data.get('order_line', [])
        
        # Format order lines for Odoo
        lines_data = []
        for line in order_lines:
            product_id = line.get('product_id')
            if not product_id:
                continue
            lines_data.append((0, 0, {
                'product_id': product_id,
                'product_uom_qty': line.get('product_uom_qty', 1),
                'price_unit': line.get('price_unit', 0)
            }))
        
        order_data = {
            'partner_id': partner_id,
            'order_line': lines_data,
        }
        
        if date_order := data.get('date_order'):
            order_data['date_order'] = date_order
        
        result = odoo_rpc_call('sale.order', 'create', [order_data])
        
        if result.get('success'):
            order_id = result.get('result')
            return jsonify({
                'success': True,
                'order_id': order_id,
                'message': f'Sales order created successfully'
            })
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error creating sales order: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/sales/quotation/<int:quotation_id>/confirm', methods=['POST'])
def confirm_quotation(quotation_id):
    """Confirm a quotation (convert to sales order)"""
    try:
        result = odoo_rpc_call('sale.order', 'action_confirm', [[quotation_id]])
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': f'Quotation {quotation_id} confirmed successfully'
            })
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error confirming quotation: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/partners', methods=['GET'])
def get_partners():
    """
    Get partners (customers/vendors).
    
    Query params:
        - search: Search by name
        - company_type: Filter by type (person, company)
        - limit: Max results (default: 100)
    """
    try:
        domain = []
        
        if search := request.args.get('search'):
            domain.append(('name', 'ilike', search))
        
        if company_type := request.args.get('company_type'):
            domain.append(('company_type', '=', company_type))
        
        limit = int(request.args.get('limit', 100))
        
        result = odoo_rpc_call('res.partner', 'search_read', [domain], {
            'fields': ['name', 'email', 'phone', 'company_type', 
                      'street', 'city', 'country_id'],
            'limit': limit
        })
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'count': len(result.get('result', [])),
                'partners': result.get('result', [])
            })
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error getting partners: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/products', methods=['GET'])
def get_products():
    """
    Get products.
    
    Query params:
        - search: Search by name
        - type: Filter by type (product, service, consurable, storable)
        - limit: Max results (default: 100)
    """
    try:
        domain = []
        
        if search := request.args.get('search'):
            domain.append(('name', 'ilike', search))
        
        if product_type := request.args.get('type'):
            domain.append(('type', '=', product_type))
        
        limit = int(request.args.get('limit', 100))
        
        result = odoo_rpc_call('product.template', 'search_read', [domain], {
            'fields': ['name', 'type', 'list_price', 'standard_price',
                      'categ_id', 'uom_id'],
            'limit': limit
        })
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'count': len(result.get('result', [])),
                'products': result.get('result', [])
            })
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/audit-log', methods=['POST'])
def log_action():
    """
    Log an action for audit trail.
    
    JSON body:
        - action: Action name (required)
        - model: Model affected
        - record_id: Record ID
        - user: User who performed action
        - details: Additional details
    """
    try:
        data = request.get_json()
        
        action = data.get('action')
        if not action:
            return jsonify({'success': False, 'error': 'action is required'}), 400
        
        # Create audit log entry
        audit_dir = Path('vault/Audit')
        audit_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'model': data.get('model', ''),
            'record_id': data.get('record_id'),
            'user': data.get('user', 'system'),
            'details': data.get('details', {}),
            'status': data.get('status', 'success')
        }
        
        # Append to daily audit log
        audit_file = audit_dir / f"audit_{datetime.now().strftime('%Y-%m-%d')}.json"
        
        audit_logs = []
        if audit_file.exists():
            import json
            with open(audit_file, 'r') as f:
                audit_logs = json.load(f)
        
        audit_logs.append(log_entry)
        
        with open(audit_file, 'w') as f:
            import json
            json.dump(audit_logs, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Action logged successfully'
        })
        
    except Exception as e:
        logger.error(f"Error logging action: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("Starting Odoo MCP Server...")
    logger.info(f"Odoo URL: {ODOO_CONFIG['url']}")
    logger.info(f"Database: {ODOO_CONFIG['db']}")
    logger.info(f"Username: {ODOO_CONFIG['username']}")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
