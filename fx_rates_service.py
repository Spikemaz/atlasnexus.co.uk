"""
FX Rates Service - Real-time currency exchange rates integration
Supports EUR, USD, GBP with automatic conversion
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import os

class FXRatesService:
    """
    Service for fetching and managing real-time FX rates
    Uses European Central Bank (ECB) as primary source
    """
    
    def __init__(self):
        self.base_currency = 'EUR'
        self.supported_currencies = ['EUR', 'USD', 'GBP']
        self.cache_file = 'data/fx_rates_cache.json'
        self.cache_duration_hours = 24
        self._rates_cache = None
        self._cache_timestamp = None
        
        # ECB API endpoint (free, reliable, no key needed)
        self.ecb_url = "https://api.frankfurter.app/latest"
        
        # Fallback: Use Exchange Rates API (free tier available)
        self.backup_url = "https://api.exchangerate-api.com/v4/latest/EUR"
        
    def get_live_rates(self) -> Dict[str, float]:
        """
        Fetch live FX rates from ECB or backup source
        Returns rates with EUR as base
        """
        try:
            # Try primary source (ECB via Frankfurter API)
            response = requests.get(
                self.ecb_url,
                params={'from': 'EUR', 'to': 'USD,GBP'},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                rates = {
                    'EUR': 1.0,
                    'USD': data['rates'].get('USD', 1.1606),  # Fallback to your Excel rates
                    'GBP': data['rates'].get('GBP', 0.8621)
                }
                self._update_cache(rates)
                return rates
                
        except Exception as e:
            print(f"Primary FX source failed: {e}")
            
        # Try backup source
        try:
            response = requests.get(self.backup_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                rates = {
                    'EUR': 1.0,
                    'USD': data['rates'].get('USD', 1.1606),
                    'GBP': data['rates'].get('GBP', 0.8621)
                }
                self._update_cache(rates)
                return rates
                
        except Exception as e:
            print(f"Backup FX source failed: {e}")
            
        # Fall back to cached or default rates
        return self._get_cached_rates()
    
    def _get_cached_rates(self) -> Dict[str, float]:
        """
        Get rates from cache or return defaults from Excel
        """
        # Check memory cache first
        if self._rates_cache and self._cache_timestamp:
            if datetime.now() - self._cache_timestamp < timedelta(hours=self.cache_duration_hours):
                return self._rates_cache
        
        # Try file cache
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    cache_time = datetime.fromisoformat(cache_data['timestamp'])
                    if datetime.now() - cache_time < timedelta(hours=self.cache_duration_hours):
                        return cache_data['rates']
            except:
                pass
        
        # Return default rates from your Excel (Tables v6)
        return {
            'EUR': 1.0,
            'USD': 1.1606,
            'GBP': 0.8621
        }
    
    def _update_cache(self, rates: Dict[str, float]):
        """
        Update both memory and file cache
        """
        self._rates_cache = rates
        self._cache_timestamp = datetime.now()
        
        # Save to file
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump({
                    'timestamp': self._cache_timestamp.isoformat(),
                    'rates': rates
                }, f, indent=2)
        except:
            pass
    
    def get_conversion_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Get full conversion matrix for all currency pairs
        Similar to your Excel Tables v6 structure
        """
        rates = self.get_live_rates()
        
        matrix = {}
        for from_curr in self.supported_currencies:
            matrix[from_curr] = {}
            for to_curr in self.supported_currencies:
                if from_curr == to_curr:
                    matrix[from_curr][to_curr] = 1.0
                else:
                    # Convert via EUR base
                    from_to_eur = 1.0 / rates[from_curr] if from_curr != 'EUR' else 1.0
                    eur_to_target = rates[to_curr] if to_curr != 'EUR' else 1.0
                    matrix[from_curr][to_curr] = from_to_eur * eur_to_target
        
        return matrix
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> Tuple[float, Dict[str, any]]:
        """
        Convert amount between currencies
        Returns: (converted_amount, metadata)
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        if from_currency == to_currency:
            return amount, {'rate': 1.0, 'source': 'direct'}
        
        if from_currency not in self.supported_currencies:
            raise ValueError(f"Currency {from_currency} not supported")
        if to_currency not in self.supported_currencies:
            raise ValueError(f"Currency {to_currency} not supported")
        
        rates = self.get_live_rates()
        
        # Convert via EUR
        if from_currency == 'EUR':
            rate = rates[to_currency]
        elif to_currency == 'EUR':
            rate = 1.0 / rates[from_currency]
        else:
            # Cross rate via EUR
            from_to_eur = 1.0 / rates[from_currency]
            eur_to_target = rates[to_currency]
            rate = from_to_eur * eur_to_target
        
        converted = amount * rate
        
        metadata = {
            'rate': rate,
            'from': from_currency,
            'to': to_currency,
            'original_amount': amount,
            'converted_amount': converted,
            'timestamp': datetime.now().isoformat(),
            'source': 'live' if self._cache_timestamp and 
                     (datetime.now() - self._cache_timestamp).seconds < 60 else 'cached'
        }
        
        return converted, metadata
    
    def format_currency(self, amount: float, currency: str) -> str:
        """
        Format amount with appropriate currency symbol
        """
        symbols = {
            'EUR': '€',
            'USD': '$',
            'GBP': '£'
        }
        symbol = symbols.get(currency.upper(), currency.upper() + ' ')
        return f"{symbol}{amount:,.2f}"
    
    def get_rates_summary(self) -> Dict:
        """
        Get a summary of current rates for display
        Matches the format in Tables v6 Excel
        """
        rates = self.get_live_rates()
        matrix = self.get_conversion_matrix()
        
        return {
            'status': 'Live ECB' if self._cache_timestamp and 
                     (datetime.now() - self._cache_timestamp).seconds < 3600 else 'Cached',
            'timestamp': datetime.now().isoformat(),
            'base_rates': rates,
            'conversion_matrix': matrix,
            'formatted_matrix': {
                'EUR_to_USD': f"1 EUR = {rates['USD']:.4f} USD",
                'EUR_to_GBP': f"1 EUR = {rates['GBP']:.4f} GBP",
                'USD_to_EUR': f"1 USD = {matrix['USD']['EUR']:.4f} EUR",
                'USD_to_GBP': f"1 USD = {matrix['USD']['GBP']:.4f} GBP",
                'GBP_to_EUR': f"1 GBP = {matrix['GBP']['EUR']:.4f} EUR",
                'GBP_to_USD': f"1 GBP = {matrix['GBP']['USD']:.4f} USD"
            }
        }


# Singleton instance
fx_service = FXRatesService()

def get_fx_rates():
    """Convenience function to get current rates"""
    return fx_service.get_live_rates()

def convert_currency(amount, from_curr, to_curr):
    """Convenience function for currency conversion"""
    return fx_service.convert(amount, from_curr, to_curr)