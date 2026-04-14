"""
AI Provider Manager with Auto-Failover
Manages multiple AI providers (Gemini, OpenRouter) with automatic switching.

Priority:
1. Gemini API (Free) - Primary
2. OpenRouter API (Paid) - Backup (auto-activates when Gemini quota exhausted)
"""

import os
import time
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class AIResponse:
    """Standardized response from any AI provider"""
    success: bool
    text: str
    model: str
    provider: str
    usage: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    is_quota_error: bool = False


class GeminiProvider:
    """Google Gemini API Provider"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model
        self._client = None
    
    @property
    def provider_name(self) -> str:
        return "gemini"
    
    def _initialize_client(self):
        """Initialize Gemini client"""
        from google import genai
        self._client = genai.Client(api_key=self.api_key)
        return self._client
    
    def generate(self, prompt: str, max_retries: int = 3, base_delay: int = 15) -> AIResponse:
        """Generate content with retry logic"""
        import time
        from google.genai.errors import APIError
        
        if not self.api_key:
            return AIResponse(
                success=False,
                text="",
                model=self.model,
                provider=self.provider_name,
                error="API key not configured",
                is_quota_error=False
            )
        
        # Initialize client if needed
        if self._client is None:
            try:
                self._initialize_client()
            except Exception as e:
                return AIResponse(
                    success=False,
                    text="",
                    model=self.model,
                    provider=self.provider_name,
                    error=f"Failed to initialize: {str(e)}",
                    is_quota_error=False
                )
        
        # Try with retries
        for attempt in range(max_retries):
            try:
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
                
                return AIResponse(
                    success=True,
                    text=response.text.strip() if response.text else "",
                    model=self.model,
                    provider=self.provider_name
                )
                
            except APIError as e:
                error_code = getattr(e, 'code', 'UNKNOWN')
                error_msg = str(e)
                
                # Check if quota exhausted
                if error_code == 429 or 'RESOURCE_EXHAUSTED' in error_msg or 'quota' in error_msg.lower():
                    if attempt < max_retries - 1:
                        wait_time = base_delay * (attempt + 1)
                        logger.warning(f"Gemini quota hit, waiting {wait_time}s before retry ({attempt + 1}/{max_retries})...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return AIResponse(
                            success=False,
                            text="",
                            model=self.model,
                            provider=self.provider_name,
                            error=f"Quota exhausted: {error_msg}",
                            is_quota_error=True
                        )
                else:
                    return AIResponse(
                        success=False,
                        text="",
                        model=self.model,
                        provider=self.provider_name,
                        error=f"API Error {error_code}: {error_msg}",
                        is_quota_error=False
                    )
                    
            except Exception as e:
                return AIResponse(
                    success=False,
                    text="",
                    model=self.model,
                    provider=self.provider_name,
                    error=f"{type(e).__name__}: {str(e)}",
                    is_quota_error=False
                )
        
        # All retries exhausted
        return AIResponse(
            success=False,
            text="",
            model=self.model,
            provider=self.provider_name,
            error=f"All {max_retries} retries exhausted",
            is_quota_error=True
        )
    
    def test_connection(self) -> AIResponse:
        """Test if Gemini API is working"""
        response = self.generate("Respond with exactly: ACTIVE", max_retries=1)
        if response.success and "ACTIVE" in response.text.upper():
            return AIResponse(
                success=True,
                text="Connection successful",
                model=self.model,
                provider=self.provider_name
            )
        return response


class OpenRouterProvider:
    """OpenRouter API Provider (supports Claude, GPT-4, Gemini, etc.)"""
    
    def __init__(self, api_key: str, model: str = "google/gemini-2.0-flash-001"):
        self.api_key = api_key
        self.model = model
        self._client = None
    
    @property
    def provider_name(self) -> str:
        return "openrouter"
    
    def _initialize_client(self):
        """Initialize OpenRouter client (uses OpenAI-compatible API)"""
        try:
            from openai import OpenAI
            self._client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key
            )
            return self._client
        except ImportError:
            # Fallback to requests if openai not installed
            import requests
            self._client = requests
            return self._client
    
    def generate(self, prompt: str, max_retries: int = 3, base_delay: int = 15) -> AIResponse:
        """Generate content via OpenRouter"""
        import time
        
        if not self.api_key:
            return AIResponse(
                success=False,
                text="",
                model=self.model,
                provider=self.provider_name,
                error="API key not configured",
                is_quota_error=False
            )
        
        # Initialize client if needed
        if self._client is None:
            try:
                self._initialize_client()
            except Exception as e:
                return AIResponse(
                    success=False,
                    text="",
                    model=self.model,
                    provider=self.provider_name,
                    error=f"Failed to initialize: {str(e)}",
                    is_quota_error=False
                )
        
        # Try with retries
        for attempt in range(max_retries):
            try:
                # Check which client we have
                if hasattr(self._client, 'chat'):
                    # OpenAI client
                    response = self._client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=4000
                    )
                    text = response.choices[0].message.content.strip() if response.choices else ""
                    
                    return AIResponse(
                        success=True,
                        text=text,
                        model=self.model,
                        provider=self.provider_name,
                        usage={
                            'prompt_tokens': response.usage.prompt_tokens if response.usage else 0,
                            'completion_tokens': response.usage.completion_tokens if response.usage else 0
                        }
                    )
                else:
                    # Requests client (fallback)
                    import requests
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "HTTP-Referer": "https://github.com/your-app",
                            "X-Title": "Silver Tier AI"
                        },
                        json={
                            "model": self.model,
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": 4000
                        },
                        timeout=60
                    )
                    response.raise_for_status()
                    data = response.json()
                    text = data['choices'][0]['message']['content'].strip()
                    
                    return AIResponse(
                        success=True,
                        text=text,
                        model=self.model,
                        provider=self.provider_name,
                        usage=data.get('usage', {})
                    )
                    
            except Exception as e:
                error_msg = str(e)
                
                # Check if it's a quota/billing error
                if 'credit' in error_msg.lower() or 'balance' in error_msg.lower():
                    return AIResponse(
                        success=False,
                        text="",
                        model=self.model,
                        provider=self.provider_name,
                        error=f"Insufficient credits: {error_msg}",
                        is_quota_error=True
                    )
                
                if attempt < max_retries - 1:
                    wait_time = base_delay * (attempt + 1)
                    logger.warning(f"OpenRouter error, retrying in {wait_time}s ({attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    return AIResponse(
                        success=False,
                        text="",
                        model=self.model,
                        provider=self.provider_name,
                        error=f"{type(e).__name__}: {error_msg}",
                        is_quota_error=False
                    )
        
        # All retries exhausted
        return AIResponse(
            success=False,
            text="",
            model=self.model,
            provider=self.provider_name,
            error=f"All {max_retries} retries exhausted",
            is_quota_error=True
        )
    
    def test_connection(self) -> AIResponse:
        """Test if OpenRouter API is working"""
        response = self.generate("Respond with exactly: ACTIVE", max_retries=1)
        if response.success and "ACTIVE" in response.text.upper():
            return AIResponse(
                success=True,
                text="Connection successful",
                model=self.model,
                provider=self.provider_name
            )
        return response


class ProviderManager:
    """
    Manages multiple AI providers with automatic failover.
    
    Modes:
    - auto: Try Gemini first, fallback to OpenRouter if quota exhausted
    - gemini: Use only Gemini
    - openrouter: Use only OpenRouter
    """
    
    def __init__(self):
        # Load configuration
        self.mode = os.getenv('AI_PROVIDER', 'auto').lower()
        self.gemini_key = os.getenv('GEMINI_API_KEY', '')
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY', '')
        self.openrouter_model = os.getenv('OPENROUTER_MODEL', 'google/gemini-2.0-flash-001')
        
        # Initialize providers
        self.gemini = None
        self.openrouter = None
        
        if self.gemini_key:
            self.gemini = GeminiProvider(self.gemini_key)
            logger.info(f"Gemini provider initialized (Key: {self.gemini_key[:10]}...)")
        else:
            logger.warning("Gemini API key not configured")
        
        if self.openrouter_key:
            self.openrouter = OpenRouterProvider(self.openrouter_key, self.openrouter_model)
            logger.info(f"OpenRouter provider initialized (Key: {self.openrouter_key[:15]}...)")
        else:
            logger.warning("OpenRouter API key not configured")
        
        # Track which provider is active
        self.current_provider = None
        self.gemini_exhausted = False
    
    def generate(self, prompt: str, max_retries: int = 3) -> AIResponse:
        """
        Generate content using configured provider(s).
        
        In 'auto' mode:
        1. Try Gemini first
        2. If Gemini quota exhausted, switch to OpenRouter
        3. Return error if both fail
        """
        
        logger.info("=" * 50)
        logger.info(f"AI Provider Mode: {self.mode}")
        logger.info("=" * 50)
        
        # Mode: gemini (only Gemini)
        if self.mode == 'gemini':
            if not self.gemini:
                return AIResponse(
                    success=False,
                    text="",
                    model="none",
                    provider="none",
                    error="Gemini provider not configured"
                )
            
            logger.info("Using Gemini provider (configured mode)")
            response = self.gemini.generate(prompt, max_retries)
            
            if response.is_quota_error:
                self.gemini_exhausted = True
                logger.warning("Gemini quota exhausted!")
            
            return response
        
        # Mode: openrouter (only OpenRouter)
        elif self.mode == 'openrouter':
            if not self.openrouter:
                return AIResponse(
                    success=False,
                    text="",
                    model="none",
                    provider="none",
                    error="OpenRouter provider not configured"
                )
            
            logger.info("Using OpenRouter provider (configured mode)")
            return self.openrouter.generate(prompt, max_retries)
        
        # Mode: auto (Gemini first, then OpenRouter)
        else:  # auto
            # Try Gemini first (if not already exhausted)
            if self.gemini and not self.gemini_exhausted:
                logger.info("Attempting Gemini API (primary)...")
                response = self.gemini.generate(prompt, max_retries)
                
                if response.success:
                    logger.info(f"✅ Gemini SUCCESS (Provider: {response.provider})")
                    self.current_provider = "gemini"
                    return response
                
                if response.is_quota_error:
                    logger.warning("⚠️ Gemini quota exhausted, switching to OpenRouter...")
                    self.gemini_exhausted = True
                    # Fall through to OpenRouter
                else:
                    logger.error(f"❌ Gemini failed: {response.error}")
                    return response
            
            # Fallback to OpenRouter
            if self.openrouter:
                logger.info("Attempting OpenRouter API (backup)...")
                response = self.openrouter.generate(prompt, max_retries)
                
                if response.success:
                    logger.info(f"✅ OpenRouter SUCCESS (Provider: {response.provider})")
                    self.current_provider = "openrouter"
                    return response
                else:
                    logger.error(f"❌ OpenRouter failed: {response.error}")
                    return response
            
            # Both failed or not configured
            return AIResponse(
                success=False,
                text="",
                model="none",
                provider="none",
                error="No providers available (Gemini exhausted, OpenRouter not configured)"
            )
    
    def test_all_providers(self) -> Dict[str, AIResponse]:
        """Test all configured providers"""
        results = {}
        
        if self.gemini:
            logger.info("Testing Gemini API...")
            results['gemini'] = self.gemini.test_connection()
            logger.info(f"Gemini: [OK] PASS" if results['gemini'].success else f"Gemini: [FAIL]")
        
        if self.openrouter:
            logger.info("Testing OpenRouter API...")
            results['openrouter'] = self.openrouter.test_connection()
            logger.info(f"OpenRouter: [OK] PASS" if results['openrouter'].success else f"OpenRouter: [FAIL]")
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get current provider status"""
        return {
            'mode': self.mode,
            'gemini_configured': self.gemini is not None,
            'openrouter_configured': self.openrouter is not None,
            'gemini_exhausted': self.gemini_exhausted,
            'current_provider': self.current_provider,
            'providers': {
                'gemini': {
                    'model': self.gemini.model if self.gemini else None,
                    'key_loaded': bool(self.gemini_key)
                },
                'openrouter': {
                    'model': self.openrouter_model if self.openrouter else None,
                    'key_loaded': bool(self.openrouter_key)
                }
            }
        }


# Global instance
_provider_manager: Optional[ProviderManager] = None


def get_provider_manager() -> ProviderManager:
    """Get or create the global provider manager instance"""
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = ProviderManager()
    return _provider_manager


def generate_ai_response(prompt: str) -> AIResponse:
    """Convenience function to generate AI response"""
    manager = get_provider_manager()
    return manager.generate(prompt)


def initialize_providers() -> Dict[str, Any]:
    """Initialize and test all providers"""
    manager = get_provider_manager()
    status = manager.get_status()
    
    logger.info("=" * 60)
    logger.info("AI PROVIDER INITIALIZATION")
    logger.info("=" * 60)
    logger.info(f"Mode: {status['mode']}")
    logger.info(f"Gemini Configured: {status['gemini_configured']}")
    logger.info(f"OpenRouter Configured: {status['openrouter_configured']}")
    
    # Test providers
    if status['gemini_configured'] or status['openrouter_configured']:
        test_results = manager.test_all_providers()
        status['test_results'] = {
            k: {'success': v.success, 'error': v.error}
            for k, v in test_results.items()
        }
    
    logger.info("=" * 60)
    
    return status


if __name__ == "__main__":
    # Test the provider manager
    print("\n" + "=" * 60)
    print("AI PROVIDER MANAGER - TEST")
    print("=" * 60 + "\n")
    
    # Initialize
    status = initialize_providers()
    
    print("\nProvider Status:")
    print(f"  Mode: {status['mode']}")
    print(f"  Gemini: [OK] Configured" if status['gemini_configured'] else "  Gemini: [FAIL] Not Configured")
    print(f"  OpenRouter: [OK] Configured" if status['openrouter_configured'] else "  OpenRouter: [FAIL] Not Configured")
    
    # Test generation
    print("\nTesting AI generation...")
    response = generate_ai_response("Respond with exactly: TEST_SUCCESS")
    
    print(f"\nResult:")
    print(f"  Success: {response.success}")
    print(f"  Provider: {response.provider}")
    print(f"  Model: {response.model}")
    print(f"  Text: {response.text[:100]}...")
    
    if response.error:
        print(f"  Error: {response.error}")
