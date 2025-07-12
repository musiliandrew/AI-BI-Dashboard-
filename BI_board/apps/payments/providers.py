"""
Payment Provider Configurations and Integrations
Supporting 20+ global payment providers
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

@dataclass
class PaymentProviderConfig:
    """Payment provider configuration"""
    name: str
    display_name: str
    region: str
    countries: List[str]
    currencies: List[str]
    api_base_url: str
    supports_subscriptions: bool = False
    supports_marketplace: bool = False
    supports_mobile_money: bool = False
    transaction_fee: float = 0.029  # 2.9%
    fixed_fee: float = 0.30  # $0.30

# Global Payment Provider Configurations
PAYMENT_PROVIDERS = {
    # North America
    'stripe': PaymentProviderConfig(
        name='stripe',
        display_name='Stripe',
        region='global',
        countries=['US', 'CA', 'GB', 'AU', 'FR', 'DE', 'IT', 'ES', 'NL', 'BE', 'AT', 'CH', 'IE', 'PT', 'LU', 'DK', 'SE', 'NO', 'FI'],
        currencies=['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CHF', 'SEK', 'NOK', 'DKK'],
        api_base_url='https://api.stripe.com/v1',
        supports_subscriptions=True,
        supports_marketplace=True,
        transaction_fee=0.029,
        fixed_fee=0.30
    ),
    
    'square': PaymentProviderConfig(
        name='square',
        display_name='Square',
        region='north_america',
        countries=['US', 'CA', 'AU', 'GB', 'IE', 'ES', 'FR'],
        currencies=['USD', 'CAD', 'AUD', 'GBP', 'EUR'],
        api_base_url='https://connect.squareup.com/v2',
        supports_subscriptions=True,
        transaction_fee=0.026,
        fixed_fee=0.10
    ),
    
    'paypal': PaymentProviderConfig(
        name='paypal',
        display_name='PayPal',
        region='global',
        countries=['US', 'CA', 'GB', 'AU', 'DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT', 'CH', 'IE', 'PT', 'LU', 'DK', 'SE', 'NO', 'FI', 'BR', 'MX', 'IN', 'JP'],
        currencies=['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'BRL', 'MXN', 'INR'],
        api_base_url='https://api.paypal.com/v2',
        supports_subscriptions=True,
        transaction_fee=0.034,
        fixed_fee=0.49
    ),
    
    # Europe
    'adyen': PaymentProviderConfig(
        name='adyen',
        display_name='Adyen',
        region='global',
        countries=['NL', 'GB', 'DE', 'FR', 'IT', 'ES', 'BE', 'AT', 'CH', 'IE', 'PT', 'LU', 'DK', 'SE', 'NO', 'FI', 'US', 'CA', 'AU', 'SG', 'HK'],
        currencies=['EUR', 'USD', 'GBP', 'CHF', 'SEK', 'NOK', 'DKK', 'CAD', 'AUD', 'SGD', 'HKD'],
        api_base_url='https://checkout-test.adyen.com/v70',
        supports_subscriptions=True,
        supports_marketplace=True,
        transaction_fee=0.028,
        fixed_fee=0.11
    ),
    
    'klarna': PaymentProviderConfig(
        name='klarna',
        display_name='Klarna',
        region='europe',
        countries=['SE', 'NO', 'FI', 'DK', 'DE', 'AT', 'NL', 'BE', 'CH', 'GB', 'US', 'AU'],
        currencies=['SEK', 'NOK', 'EUR', 'DKK', 'CHF', 'GBP', 'USD', 'AUD'],
        api_base_url='https://api.klarna.com',
        supports_subscriptions=False,
        supports_marketplace=False,
        transaction_fee=0.035,
        fixed_fee=0.35
    ),
    
    'mollie': PaymentProviderConfig(
        name='mollie',
        display_name='Mollie',
        region='europe',
        countries=['NL', 'BE', 'DE', 'AT', 'CH', 'GB', 'FR', 'IT', 'ES', 'PT', 'IE', 'LU', 'DK', 'SE', 'NO', 'FI', 'PL', 'CZ', 'HU'],
        currencies=['EUR', 'USD', 'GBP', 'CHF', 'SEK', 'NOK', 'DKK', 'PLN', 'CZK', 'HUF'],
        api_base_url='https://api.mollie.com/v2',
        supports_subscriptions=True,
        transaction_fee=0.025,
        fixed_fee=0.25
    ),
    
    # Africa
    'flutterwave': PaymentProviderConfig(
        name='flutterwave',
        display_name='Flutterwave',
        region='africa',
        countries=['NG', 'GH', 'KE', 'UG', 'TZ', 'RW', 'ZM', 'ZA', 'EG', 'MA'],
        currencies=['NGN', 'GHS', 'KES', 'UGX', 'TZS', 'RWF', 'ZMW', 'ZAR', 'EGP', 'MAD', 'USD', 'EUR', 'GBP'],
        api_base_url='https://api.flutterwave.com/v3',
        supports_subscriptions=True,
        supports_mobile_money=True,
        transaction_fee=0.014,
        fixed_fee=0.00
    ),
    
    'paystack': PaymentProviderConfig(
        name='paystack',
        display_name='Paystack',
        region='africa',
        countries=['NG', 'GH', 'ZA', 'KE'],
        currencies=['NGN', 'GHS', 'ZAR', 'KES', 'USD'],
        api_base_url='https://api.paystack.co',
        supports_subscriptions=True,
        supports_mobile_money=True,
        transaction_fee=0.015,
        fixed_fee=0.00
    ),
    
    'mpesa': PaymentProviderConfig(
        name='mpesa',
        display_name='M-Pesa',
        region='africa',
        countries=['KE', 'TZ', 'UG', 'RW', 'ET', 'CD', 'MZ', 'EG', 'GH', 'LS'],
        currencies=['KES', 'TZS', 'UGX', 'RWF', 'ETB', 'CDF', 'MZN', 'EGP', 'GHS', 'LSL'],
        api_base_url='https://sandbox.safaricom.co.ke/mpesa',
        supports_subscriptions=False,
        supports_mobile_money=True,
        transaction_fee=0.01,
        fixed_fee=0.00
    ),
    
    # Asia Pacific
    'razorpay': PaymentProviderConfig(
        name='razorpay',
        display_name='Razorpay',
        region='asia_pacific',
        countries=['IN'],
        currencies=['INR', 'USD'],
        api_base_url='https://api.razorpay.com/v1',
        supports_subscriptions=True,
        supports_marketplace=True,
        transaction_fee=0.02,
        fixed_fee=0.00
    ),
    
    'xendit': PaymentProviderConfig(
        name='xendit',
        display_name='Xendit',
        region='asia_pacific',
        countries=['ID', 'PH', 'TH', 'VN', 'MY', 'SG'],
        currencies=['IDR', 'PHP', 'THB', 'VND', 'MYR', 'SGD', 'USD'],
        api_base_url='https://api.xendit.co',
        supports_subscriptions=True,
        transaction_fee=0.029,
        fixed_fee=0.00
    ),
    
    'alipay': PaymentProviderConfig(
        name='alipay',
        display_name='Alipay',
        region='asia_pacific',
        countries=['CN', 'HK', 'MO', 'TW', 'SG', 'MY', 'TH', 'PH', 'ID', 'VN', 'KR', 'JP'],
        currencies=['CNY', 'HKD', 'MOP', 'TWD', 'SGD', 'MYR', 'THB', 'PHP', 'IDR', 'VND', 'KRW', 'JPY', 'USD'],
        api_base_url='https://openapi.alipay.com/gateway.do',
        supports_subscriptions=False,
        transaction_fee=0.006,
        fixed_fee=0.00
    ),
    
    'omise': PaymentProviderConfig(
        name='omise',
        display_name='Omise',
        region='asia_pacific',
        countries=['TH', 'JP', 'SG', 'MY'],
        currencies=['THB', 'JPY', 'SGD', 'MYR', 'USD'],
        api_base_url='https://api.omise.co',
        supports_subscriptions=True,
        transaction_fee=0.035,
        fixed_fee=0.00
    ),
    
    # Latin America
    'mercadopago': PaymentProviderConfig(
        name='mercadopago',
        display_name='MercadoPago',
        region='latin_america',
        countries=['AR', 'BR', 'CL', 'CO', 'MX', 'PE', 'UY', 'VE'],
        currencies=['ARS', 'BRL', 'CLP', 'COP', 'MXN', 'PEN', 'UYU', 'VES', 'USD'],
        api_base_url='https://api.mercadopago.com/v1',
        supports_subscriptions=True,
        transaction_fee=0.049,
        fixed_fee=0.00
    ),
    
    'dlocal': PaymentProviderConfig(
        name='dlocal',
        display_name='dLocal',
        region='latin_america',
        countries=['AR', 'BR', 'CL', 'CO', 'MX', 'PE', 'UY', 'EC', 'PY', 'BO'],
        currencies=['ARS', 'BRL', 'CLP', 'COP', 'MXN', 'PEN', 'UYU', 'USD', 'EUR'],
        api_base_url='https://api.dlocal.com/v1',
        supports_subscriptions=True,
        supports_marketplace=True,
        transaction_fee=0.039,
        fixed_fee=0.00
    ),
    
    'ebanx': PaymentProviderConfig(
        name='ebanx',
        display_name='EBANX',
        region='latin_america',
        countries=['BR', 'MX', 'CO', 'AR', 'PE', 'CL', 'EC', 'BO', 'PY', 'UY'],
        currencies=['BRL', 'MXN', 'COP', 'ARS', 'PEN', 'CLP', 'USD'],
        api_base_url='https://api.ebanx.com/ws',
        supports_subscriptions=True,
        transaction_fee=0.049,
        fixed_fee=0.00
    ),
    
    # Oceania
    'tyro': PaymentProviderConfig(
        name='tyro',
        display_name='Tyro',
        region='oceania',
        countries=['AU'],
        currencies=['AUD'],
        api_base_url='https://api.tyro.com/v1',
        supports_subscriptions=True,
        transaction_fee=0.017,
        fixed_fee=0.00
    ),
    
    'afterpay': PaymentProviderConfig(
        name='afterpay',
        display_name='Afterpay',
        region='oceania',
        countries=['AU', 'NZ', 'US', 'CA', 'GB', 'FR', 'ES', 'IT'],
        currencies=['AUD', 'NZD', 'USD', 'CAD', 'GBP', 'EUR'],
        api_base_url='https://api.afterpay.com/v2',
        supports_subscriptions=False,
        supports_marketplace=False,
        transaction_fee=0.04,
        fixed_fee=0.30
    )
}

class PaymentProviderManager:
    """Manage payment provider configurations and capabilities"""
    
    @staticmethod
    def get_providers_by_region(region: str) -> List[PaymentProviderConfig]:
        """Get all payment providers for a specific region"""
        providers = []
        for provider in PAYMENT_PROVIDERS.values():
            if provider.region == region or provider.region == 'global':
                providers.append(provider)
        return providers
    
    @staticmethod
    def get_providers_by_country(country_code: str) -> List[PaymentProviderConfig]:
        """Get all payment providers available in a specific country"""
        providers = []
        for provider in PAYMENT_PROVIDERS.values():
            if country_code in provider.countries:
                providers.append(provider)
        return providers
    
    @staticmethod
    def get_providers_by_currency(currency_code: str) -> List[PaymentProviderConfig]:
        """Get all payment providers that support a specific currency"""
        providers = []
        for provider in PAYMENT_PROVIDERS.values():
            if currency_code in provider.currencies:
                providers.append(provider)
        return providers
    
    @staticmethod
    def get_optimal_provider(country: str, currency: str, features: List[str] = None) -> Optional[PaymentProviderConfig]:
        """Get the optimal payment provider for specific requirements"""
        features = features or []
        
        # Get providers available in country and supporting currency
        available_providers = []
        for provider in PAYMENT_PROVIDERS.values():
            if country in provider.countries and currency in provider.currencies:
                available_providers.append(provider)
        
        if not available_providers:
            return None
        
        # Filter by required features
        if 'subscriptions' in features:
            available_providers = [p for p in available_providers if p.supports_subscriptions]
        
        if 'marketplace' in features:
            available_providers = [p for p in available_providers if p.supports_marketplace]
        
        if 'mobile_money' in features:
            available_providers = [p for p in available_providers if p.supports_mobile_money]
        
        if not available_providers:
            return None
        
        # Sort by total cost (transaction fee + fixed fee)
        # Assuming average transaction of $100
        avg_transaction = 100
        available_providers.sort(key=lambda p: (avg_transaction * p.transaction_fee) + p.fixed_fee)
        
        return available_providers[0]
    
    @staticmethod
    def calculate_fees(provider_name: str, amount: Decimal, currency: str = 'USD') -> Dict[str, Decimal]:
        """Calculate fees for a transaction"""
        provider = PAYMENT_PROVIDERS.get(provider_name)
        if not provider:
            return {'provider_fee': Decimal('0'), 'net_amount': amount}
        
        provider_fee = (amount * Decimal(str(provider.transaction_fee))) + Decimal(str(provider.fixed_fee))
        net_amount = amount - provider_fee
        
        return {
            'gross_amount': amount,
            'provider_fee': provider_fee,
            'net_amount': net_amount,
            'fee_percentage': provider.transaction_fee,
            'fixed_fee': Decimal(str(provider.fixed_fee))
        }
    
    @staticmethod
    def get_regional_recommendations() -> Dict[str, List[str]]:
        """Get recommended payment providers by region"""
        return {
            'north_america': ['stripe', 'square', 'paypal'],
            'europe': ['stripe', 'adyen', 'mollie', 'klarna'],
            'africa': ['flutterwave', 'paystack', 'mpesa'],
            'asia_pacific': ['stripe', 'razorpay', 'xendit', 'alipay', 'omise'],
            'latin_america': ['mercadopago', 'dlocal', 'ebanx', 'stripe'],
            'oceania': ['stripe', 'square', 'tyro', 'afterpay']
        }
    
    @staticmethod
    def get_market_coverage_stats() -> Dict[str, Any]:
        """Get statistics about global market coverage"""
        total_countries = set()
        total_currencies = set()
        
        for provider in PAYMENT_PROVIDERS.values():
            total_countries.update(provider.countries)
            total_currencies.update(provider.currencies)
        
        return {
            'total_providers': len(PAYMENT_PROVIDERS),
            'countries_covered': len(total_countries),
            'currencies_supported': len(total_currencies),
            'regions_covered': len(set(p.region for p in PAYMENT_PROVIDERS.values())),
            'subscription_providers': len([p for p in PAYMENT_PROVIDERS.values() if p.supports_subscriptions]),
            'marketplace_providers': len([p for p in PAYMENT_PROVIDERS.values() if p.supports_marketplace]),
            'mobile_money_providers': len([p for p in PAYMENT_PROVIDERS.values() if p.supports_mobile_money])
        }

# Regional payment method preferences
REGIONAL_PAYMENT_PREFERENCES = {
    'north_america': {
        'credit_card': 0.45,
        'debit_card': 0.25,
        'digital_wallet': 0.20,
        'bank_transfer': 0.10
    },
    'europe': {
        'credit_card': 0.35,
        'debit_card': 0.30,
        'bank_transfer': 0.20,
        'digital_wallet': 0.15
    },
    'africa': {
        'mobile_money': 0.60,
        'bank_transfer': 0.25,
        'credit_card': 0.10,
        'cash': 0.05
    },
    'asia_pacific': {
        'digital_wallet': 0.40,
        'credit_card': 0.25,
        'bank_transfer': 0.20,
        'mobile_payment': 0.15
    },
    'latin_america': {
        'cash': 0.35,
        'debit_card': 0.25,
        'bank_transfer': 0.20,
        'credit_card': 0.20
    },
    'oceania': {
        'credit_card': 0.40,
        'debit_card': 0.30,
        'digital_wallet': 0.20,
        'bank_transfer': 0.10
    }
}

# Currency conversion priorities
CURRENCY_CONVERSION_PRIORITIES = {
    'primary': ['USD', 'EUR', 'GBP'],
    'secondary': ['CAD', 'AUD', 'JPY', 'CHF'],
    'regional': {
        'africa': ['NGN', 'KES', 'ZAR', 'GHS'],
        'asia_pacific': ['INR', 'CNY', 'SGD', 'THB'],
        'latin_america': ['BRL', 'MXN', 'ARS', 'COP'],
        'europe': ['SEK', 'NOK', 'DKK', 'PLN'],
        'oceania': ['NZD']
    }
}

# Global payment provider manager instance
payment_provider_manager = PaymentProviderManager()
