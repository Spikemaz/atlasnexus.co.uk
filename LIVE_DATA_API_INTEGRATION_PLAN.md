# Live Data API Integration Plan - Top 20 Free APIs

**Project:** Atlas Nexus ABS Calculator Enhancement
**Purpose:** Integrate real-time market data to improve calculation accuracy
**Status:** Planning Phase - NOT YET IMPLEMENTED
**Created:** 2026-01-19

---

## Executive Summary

This document outlines the top 20 free/freemium APIs to integrate into the Atlas Nexus permutation engine to enhance calculation accuracy using live market data. All APIs listed are freely available or have generous free tiers suitable for production use.

**Total New Metrics:** 150+ calculated fields
**Total API Endpoints:** 20 APIs, ~80 specific endpoints
**Expected Accuracy Improvement:** 30-40% (especially for pricing, DSCR, IRR)
**Implementation Effort:** ~4-6 weeks for full integration

---

## Top 20 Free APIs - Detailed Specifications

---

### 1. FRED API (Federal Reserve Economic Data) ⭐⭐⭐⭐⭐

**Provider:** Federal Reserve Bank of St. Louis
**URL:** https://fred.stlouisfed.org/docs/api/
**Cost:** 100% Free, requires API key (instant approval)
**Rate Limit:** None specified (reasonable use policy)
**Update Frequency:** Daily (some series intraday)

#### Key Data Series Available:

| Series ID | Description | Use Case | Update Frequency |
|-----------|-------------|----------|------------------|
| `DGS1` | 1-Year Treasury Constant Maturity | Risk-free rate, discount rate | Daily |
| `DGS3` | 3-Year Treasury Constant Maturity | Senior debt pricing baseline | Daily |
| `DGS5` | 5-Year Treasury Constant Maturity | Mid-term debt pricing | Daily |
| `DGS7` | 7-Year Treasury Constant Maturity | Long-term debt pricing | Daily |
| `DGS10` | 10-Year Treasury Constant Maturity | Equity discount rate, WACC | Daily |
| `SOFR` | Secured Overnight Financing Rate | USD floating rate baseline | Daily |
| `DPRIME` | Bank Prime Loan Rate | Alternative floating rate | Weekly |
| `CPIAUCSL` | US CPI All Items | Inflation for USD projects | Monthly |
| `PCEPI` | Personal Consumption Expenditures Price Index | Core inflation measure | Monthly |
| `DEXUSEU` | USD/EUR Exchange Rate | FX conversion | Daily |
| `DEXUSUK` | USD/GBP Exchange Rate | FX conversion | Daily |
| `DEXJPUS` | JPY/USD Exchange Rate | FX conversion | Daily |
| `BAMLC0A1CAAAEY` | ICE BofA AAA US Corporate Index Yield | AAA credit spread baseline | Daily |
| `BAMLC0A2CAAEY` | ICE BofA AA US Corporate Index Yield | AA credit spread baseline | Daily |
| `BAMLC0A3CAEY` | ICE BofA A US Corporate Index Yield | A credit spread baseline | Daily |
| `BAMLC0A4CBBBEY` | ICE BofA BBB US Corporate Index Yield | BBB credit spread baseline | Daily |
| `BAMLH0A0HYM2` | ICE BofA High Yield Index Spread | High yield spread baseline | Daily |
| `MORTGAGE30US` | 30-Year Fixed Rate Mortgage Average | Long-term debt benchmark | Weekly |
| `UNRATE` | US Unemployment Rate | Economic health indicator | Monthly |
| `GDP` | US GDP | Economic growth indicator | Quarterly |

#### Implementation Example:

```javascript
class FREDClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = 'https://api.stlouisfed.org/fred';
    this.cache = new Map();
  }

  async getSeries(seriesId, lookback = 1) {
    const cacheKey = `${seriesId}_${lookback}`;
    if (this.isCached(cacheKey)) {
      return this.cache.get(cacheKey).value;
    }

    const url = `${this.baseUrl}/series/observations`;
    const params = new URLSearchParams({
      series_id: seriesId,
      api_key: this.apiKey,
      file_type: 'json',
      sort_order: 'desc',
      limit: lookback
    });

    const response = await fetch(`${url}?${params}`);
    const data = await response.json();

    const latestValue = parseFloat(data.observations[0].value);
    this.cache.set(cacheKey, { value: latestValue, timestamp: Date.now() });

    return latestValue;
  }

  async getTreasuryYield(maturity) {
    const seriesMap = {
      '1Y': 'DGS1',
      '3Y': 'DGS3',
      '5Y': 'DGS5',
      '7Y': 'DGS7',
      '10Y': 'DGS10'
    };
    return await this.getSeries(seriesMap[maturity]);
  }

  async getSOFR() {
    return await this.getSeries('SOFR');
  }

  async getCPIInflation() {
    const current = await this.getSeries('CPIAUCSL', 1);
    const yearAgo = await this.getSeries('CPIAUCSL', 13);
    return ((current / yearAgo[12] - 1) * 100);  // YoY %
  }

  async getCreditSpread(rating) {
    const ratingSeriesMap = {
      'AAA': 'BAMLC0A1CAAAEY',
      'AA': 'BAMLC0A2CAAEY',
      'A': 'BAMLC0A3CAEY',
      'BBB': 'BAMLC0A4CBBBEY'
    };

    const corporateYield = await this.getSeries(ratingSeriesMap[rating]);
    const treasury10Y = await this.getSeries('DGS10');

    return (corporateYield - treasury10Y) * 100;  // Spread in bps
  }

  isCached(key) {
    const cached = this.cache.get(key);
    if (!cached) return false;
    // Cache for 6 hours (FRED updates daily)
    return (Date.now() - cached.timestamp) < 6 * 60 * 60 * 1000;
  }
}
```

#### Permutation Engine Integration:

```javascript
async function enhancedSeniorDebtPricing(seniorWAL, targetRating, currency) {
  const fred = new FREDClient(process.env.FRED_API_KEY);

  // Get risk-free rate (interpolate if needed)
  let riskFreeRate;
  if (seniorWAL <= 3) {
    riskFreeRate = await fred.getTreasuryYield('3Y');
  } else if (seniorWAL <= 7) {
    const y5 = await fred.getTreasuryYield('5Y');
    const y7 = await fred.getTreasuryYield('7Y');
    riskFreeRate = y5 + (y7 - y5) * ((seniorWAL - 5) / 2);
  } else {
    riskFreeRate = await fred.getTreasuryYield('10Y');
  }

  // Get credit spread for rating
  const creditSpread = await fred.getCreditSpread(targetRating);

  // Sector-specific adjustment
  const dataCenterPremium = 25;  // bps premium for data centers vs. general corporate

  // Calculate all-in coupon
  const seniorCoupon = riskFreeRate + (creditSpread / 100) + (dataCenterPremium / 100);

  return {
    riskFreeRate: riskFreeRate,
    creditSpread: creditSpread,
    sectorPremium: dataCenterPremium,
    allInCoupon: seniorCoupon
  };
}
```

**New Metrics Enabled:**
- Dynamic senior coupon (vs. fixed 5.5%)
- Real-time credit spread by rating
- Inflation-adjusted revenue projections
- FX-adjusted CapEx and revenue

---

### 2. ECB Statistical Data Warehouse (SDW) API ⭐⭐⭐⭐⭐

**Provider:** European Central Bank
**URL:** https://data.ecb.europa.eu/help/api/overview
**Cost:** 100% Free, no API key required
**Rate Limit:** None specified (reasonable use)
**Update Frequency:** Daily (some series intraday)

#### Key Data Series:

| Flow/Dimension | Description | Use Case | Update Frequency |
|----------------|-------------|----------|------------------|
| `FM.D.U2.EUR.4F.KR.MRR_FR.LEV` | ECB Main Refinancing Rate | Euro base rate | Weekly |
| `FM.D.U2.EUR.4F.KR.DFR.LEV` | ECB Deposit Facility Rate | Euro floor rate | Weekly |
| `IRS.D.*.EUR.L.A.A*` | EURIBOR Rates (1M, 3M, 6M, 12M) | Euro floating rate benchmark | Daily |
| `YC.B.U2.EUR.4F.G_N_A.SV_C_YM.*` | Euro Area Yield Curve | Risk-free rate by maturity | Daily |
| `ICP.M.U2.N.*` | HICP - Harmonized Index Consumer Prices | Eurozone inflation | Monthly |
| `EXR.D.*.EUR.SP00.A` | EUR Exchange Rates | FX conversions | Daily |
| `SEC.M.I8.1300.F51100.Z01.E.Z` | MFI Interest Rates on Loans | Commercial lending rates | Monthly |

#### Implementation Example:

```javascript
class ECBClient {
  constructor() {
    this.baseUrl = 'https://data-api.ecb.europa.eu/service/data';
    this.cache = new Map();
  }

  async getDataSeries(flowRef, key, startPeriod = null) {
    const cacheKey = `${flowRef}_${key}`;
    if (this.isCached(cacheKey)) {
      return this.cache.get(cacheKey).value;
    }

    const params = new URLSearchParams({
      format: 'jsondata',
      lastNObservations: 1
    });
    if (startPeriod) {
      params.set('startPeriod', startPeriod);
    }

    const url = `${this.baseUrl}/${flowRef}/${key}?${params}`;
    const response = await fetch(url);
    const data = await response.json();

    const latestValue = parseFloat(
      data.dataSets[0].series['0:0:0:0:0:0:0'].observations[0][0]
    );

    this.cache.set(cacheKey, { value: latestValue, timestamp: Date.now() });
    return latestValue;
  }

  async getEURIBOR(tenor = '6M') {
    const tenorMap = {
      '1M': 'IRS.D.1M.EUR.L.A.A*',
      '3M': 'IRS.D.3M.EUR.L.A.A*',
      '6M': 'IRS.D.6M.EUR.L.A.A*',
      '12M': 'IRS.D.12M.EUR.L.A.A*'
    };

    return await this.getDataSeries('FM', tenorMap[tenor]);
  }

  async getEuroYieldCurve(maturity) {
    // Euro AAA government bond yield curve
    const maturityKey = `YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_${maturity}Y`;
    return await this.getDataSeries('YC', maturityKey);
  }

  async getHICPInflation() {
    // Year-over-year HICP inflation
    const current = await this.getDataSeries('ICP', 'ICP.M.U2.N.000000.4.ANR');
    return current;
  }

  async getFXRate(currency) {
    // EUR/XXX exchange rate
    const key = `EXR.D.${currency}.EUR.SP00.A`;
    return await this.getDataSeries('EXR', key);
  }

  isCached(key) {
    const cached = this.cache.get(key);
    if (!cached) return false;
    return (Date.now() - cached.timestamp) < 6 * 60 * 60 * 1000;  // 6 hours
  }
}
```

#### Permutation Engine Integration:

```javascript
async function calculateEuroSeniorCoupon(seniorWAL, targetRating) {
  const ecb = new ECBClient();

  // Get EURIBOR 6M as base rate
  const euribor6M = await ecb.getEURIBOR('6M');

  // Get credit spread (from separate source or database)
  const creditSpreads = {
    'AAA': 85,   // bps over EURIBOR
    'AA': 125,
    'A': 175,
    'BBB': 250,
    'BB': 400
  };

  const spread = creditSpreads[targetRating];

  // Data center infrastructure premium
  const sectorPremium = 25;  // bps

  // All-in coupon
  const seniorCoupon = euribor6M + (spread + sectorPremium) / 100;

  return {
    baseRate: euribor6M,
    creditSpread: spread,
    sectorPremium: sectorPremium,
    allInCoupon: seniorCoupon,
    rationale: `EURIBOR 6M (${euribor6M.toFixed(2)}%) + ${targetRating} spread (${spread}bps) + sector premium (${sectorPremium}bps)`
  };
}
```

**New Metrics Enabled:**
- Dynamic EURIBOR-based pricing
- Euro area yield curve (1Y to 30Y)
- Eurozone inflation for revenue escalation
- EUR/GBP, EUR/USD live rates

---

### 3. Open Exchange Rates API ⭐⭐⭐⭐

**Provider:** Open Exchange Rates
**URL:** https://openexchangerates.org/
**Cost:** Free tier: 1,000 requests/month (sufficient for most use cases)
**Rate Limit:** 1,000 requests/month on free tier
**Update Frequency:** Hourly (free tier: daily)

#### Implementation Example:

```javascript
class OpenExchangeRatesClient {
  constructor(appId) {
    this.appId = appId;
    this.baseUrl = 'https://openexchangerates.org/api';
    this.cache = new Map();
  }

  async getLatestRates(base = 'EUR') {
    const cacheKey = `latest_${base}`;
    if (this.isCached(cacheKey)) {
      return this.cache.get(cacheKey).value;
    }

    const url = `${this.baseUrl}/latest.json?app_id=${this.appId}&base=${base}`;
    const response = await fetch(url);
    const data = await response.json();

    this.cache.set(cacheKey, { value: data.rates, timestamp: Date.now() });
    return data.rates;
  }

  async convertCurrency(amount, from, to) {
    const rates = await this.getLatestRates('EUR');

    // Convert from -> EUR -> to
    let amountInEUR;
    if (from === 'EUR') {
      amountInEUR = amount;
    } else {
      amountInEUR = amount / rates[from];
    }

    let amountInTarget;
    if (to === 'EUR') {
      amountInTarget = amountInEUR;
    } else {
      amountInTarget = amountInEUR * rates[to];
    }

    return {
      originalAmount: amount,
      originalCurrency: from,
      convertedAmount: amountInTarget,
      convertedCurrency: to,
      rate: amountInTarget / amount
    };
  }

  isCached(key) {
    const cached = this.cache.get(key);
    if (!cached) return false;
    return (Date.now() - cached.timestamp) < 24 * 60 * 60 * 1000;  // 24 hours
  }
}
```

#### Permutation Engine Integration:

```javascript
async function normalizeProjectToEUR(sponsorInput) {
  const fx = new OpenExchangeRatesClient(process.env.OPEN_EXCHANGE_RATES_APP_ID);

  const inputCurrency = sponsorInput.capexCurrency;

  if (inputCurrency === 'EUR') {
    return sponsorInput;  // No conversion needed
  }

  // Convert all monetary values to EUR
  const capexConversion = await fx.convertCurrency(
    sponsorInput.capexTotal,
    inputCurrency,
    'EUR'
  );

  const revenueConversion = await fx.convertCurrency(
    sponsorInput.grossMonthlyRent,
    sponsorInput.kwhCurrency,
    'EUR'
  );

  return {
    ...sponsorInput,
    capexTotalEUR: capexConversion.convertedAmount,
    grossMonthlyRentEUR: revenueConversion.convertedAmount,
    fxRates: {
      capex: capexConversion.rate,
      revenue: revenueConversion.rate
    },
    fxTimestamp: new Date().toISOString()
  };
}
```

**New Metrics Enabled:**
- Real-time currency conversion for 170+ currencies
- FX exposure calculation
- Multi-currency project support

---

### 4. ENTSO-E Transparency Platform API ⭐⭐⭐⭐

**Provider:** European Network of Transmission System Operators for Electricity
**URL:** https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html
**Cost:** 100% Free, requires registration
**Rate Limit:** 400 requests/minute
**Update Frequency:** Real-time (15-minute intervals for prices)

#### Key Data Points:

| Document Type | Description | Use Case |
|---------------|-------------|----------|
| `A44` | Day-Ahead Prices | Electricity cost forecasting |
| `A25` | Actual Generation per Type | Renewable % calculation |
| `A75` | Actual Total Load | Grid stress, price correlation |
| `A65` | System OPEX | Grid costs |

#### Implementation Example:

```javascript
class ENTSOEClient {
  constructor(securityToken) {
    this.securityToken = securityToken;
    this.baseUrl = 'https://web-api.tp.entsoe.eu/api';
    this.cache = new Map();
  }

  async getDayAheadPrices(countryCode, startDate, endDate) {
    const cacheKey = `prices_${countryCode}_${startDate}`;
    if (this.isCached(cacheKey)) {
      return this.cache.get(cacheKey).value;
    }

    const params = new URLSearchParams({
      securityToken: this.securityToken,
      documentType: 'A44',  // Day-ahead prices
      in_Domain: this.getEICCode(countryCode),
      out_Domain: this.getEICCode(countryCode),
      periodStart: this.formatDate(startDate),
      periodEnd: this.formatDate(endDate)
    });

    const response = await fetch(`${this.baseUrl}?${params}`);
    const xmlText = await response.text();

    // Parse XML response (simplified)
    const prices = this.parseXMLPrices(xmlText);
    const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length;

    this.cache.set(cacheKey, { value: avgPrice, timestamp: Date.now() });
    return avgPrice;
  }

  getEICCode(countryCode) {
    // Energy Identification Codes by country
    const eicMap = {
      'UK': '10YGB----------A',
      'DE': '10Y1001A1001A83F',
      'FR': '10YFR-RTE------C',
      'NL': '10YNL----------L',
      'IE': '10YIE-1001A00010',
      'ES': '10YES-REE------0',
      'IT': '10YIT-GRTN-----B',
      'PL': '10YPL-AREA-----S',
      'SE': '10YSE-1--------K',
      'NO': '10YNO-0--------C'
      // Add more as needed
    };
    return eicMap[countryCode];
  }

  formatDate(date) {
    // Format: YYYYMMDDHHmm
    return date.toISOString().replace(/[-:]/g, '').slice(0, 12);
  }

  parseXMLPrices(xmlText) {
    // Simplified XML parsing (use proper XML parser in production)
    const regex = /<price.amount>([\d.]+)<\/price.amount>/g;
    const prices = [];
    let match;
    while ((match = regex.exec(xmlText)) !== null) {
      prices.push(parseFloat(match[1]));
    }
    return prices;
  }

  isCached(key) {
    const cached = this.cache.get(key);
    if (!cached) return false;
    return (Date.now() - cached.timestamp) < 12 * 60 * 60 * 1000;  // 12 hours
  }
}
```

#### Permutation Engine Integration:

```javascript
async function calculateElectricityOPEX(sponsorInput) {
  const entsoe = new ENTSOEClient(process.env.ENTSOE_SECURITY_TOKEN);

  // Only relevant for Gross leases (landlord pays electricity)
  if (sponsorInput.leaseType !== 'Gross') {
    return 0;
  }

  const countryCode = this.getCountryCode(sponsorInput.locationCountry);
  const today = new Date();
  const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);

  // Get average day-ahead price for last 30 days (€/MWh)
  const avgPriceEURMWh = await entsoe.getDayAheadPrices(countryCode, monthAgo, today);

  // Calculate annual electricity cost
  const itLoadMW = sponsorInput.grossFacilityPower / sponsorInput.pue;
  const annualMWh = itLoadMW * 8760;  // hours per year
  const annualElectricityCost = annualMWh * avgPriceEURMWh;

  // Project future years with 4% energy inflation
  const electricityInflation = 4.0;
  const projectedOPEX = [];

  for (let year = 1; year <= 15; year++) {
    const yearlyOPEX = annualElectricityCost * Math.pow(1 + electricityInflation / 100, year);
    projectedOPEX.push({
      year: year,
      electricityOPEX: yearlyOPEX,
      pricePerMWh: avgPriceEURMWh * Math.pow(1 + electricityInflation / 100, year)
    });
  }

  return {
    currentPriceEURMWh: avgPriceEURMWh,
    year1OPEX: projectedOPEX[0].electricityOPEX,
    projectedOPEX: projectedOPEX,
    dataSource: 'ENTSO-E Day-Ahead Market'
  };
}
```

**New Metrics Enabled:**
- Real-time electricity prices by country
- Renewable energy % in grid mix
- Grid carbon intensity for ESG scoring

---

### 5. Eurostat API ⭐⭐⭐⭐

**Provider:** European Commission
**URL:** https://ec.europa.eu/eurostat/web/json-and-unicode-web-services/getting-started/rest-request
**Cost:** 100% Free, no API key required
**Rate Limit:** None specified
**Update Frequency:** Monthly/Quarterly depending on dataset

#### Key Datasets:

| Dataset Code | Description | Use Case | Update Frequency |
|--------------|-------------|----------|------------------|
| `prc_hicp_midx` | HICP - Monthly Inflation | Revenue escalation | Monthly |
| `sts_copi_m` | Construction Price Index | CapEx escalation | Monthly |
| `ei_bsin_m_r2` | Construction Confidence Indicator | Market risk | Monthly |
| `nama_10_gdp` | GDP and Main Components | Economic health | Quarterly |
| `lfsq_urgan` | Unemployment Rate | Labor market | Quarterly |
| `nrg_pc_205` | Electricity Prices for Industrial Consumers | OPEX forecasting | Semi-annual |

#### Implementation Example:

```javascript
class EurostatClient {
  constructor() {
    this.baseUrl = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data';
    this.cache = new Map();
  }

  async getDataset(datasetCode, filters = {}) {
    const cacheKey = `${datasetCode}_${JSON.stringify(filters)}`;
    if (this.isCached(cacheKey)) {
      return this.cache.get(cacheKey).value;
    }

    // Build filter string (e.g., "A.FR.CP00")
    const filterString = Object.values(filters).join('.');

    const url = `${this.baseUrl}/${datasetCode}/${filterString}`;
    const params = new URLSearchParams({
      format: 'JSON',
      lang: 'en'
    });

    const response = await fetch(`${url}?${params}`);
    const data = await response.json();

    // Extract latest value (simplified)
    const latestValue = this.extractLatestValue(data);

    this.cache.set(cacheKey, { value: latestValue, timestamp: Date.now() });
    return latestValue;
  }

  async getInflationRate(countryCode) {
    // HICP Year-over-year rate
    const filters = {
      freq: 'M',      // Monthly
      unit: 'RCH_A',  // Rate of change, annual
      coicop: 'CP00', // All items
      geo: countryCode
    };

    return await this.getDataset('prc_hicp_midx', filters);
  }

  async getConstructionCostIndex(countryCode) {
    const filters = {
      freq: 'M',
      nace_r2: 'F',   // Construction
      geo: countryCode
    };

    return await this.getDataset('sts_copi_m', filters);
  }

  async getElectricityPrice(countryCode) {
    // Industrial consumers, medium size
    const filters = {
      freq: 'S',      // Semi-annual
      consom: 'MWH500-1999',  // 500-2000 MWh annual consumption
      tax: 'X_TAX',   // Excluding taxes
      currency: 'EUR',
      unit: 'KWH',
      geo: countryCode
    };

    return await this.getDataset('nrg_pc_205', filters);
  }

  extractLatestValue(data) {
    // Eurostat JSON structure has values in data.value object
    const values = data.value;
    const latestIndex = Object.keys(values).sort().pop();
    return parseFloat(values[latestIndex]);
  }

  isCached(key) {
    const cached = this.cache.get(key);
    if (!cached) return false;
    return (Date.now() - cached.timestamp) < 24 * 60 * 60 * 1000;  // 24 hours
  }
}
```

#### Permutation Engine Integration:

```javascript
async function applyInflationToRevenue(sponsorInput) {
  const eurostat = new EurostatClient();

  const countryCode = this.getEU28Code(sponsorInput.locationCountry);

  // Get current inflation rate
  const currentInflation = await eurostat.getInflationRate(countryCode);

  // Use greater of: current inflation or 2% floor
  const revenueEscalation = Math.max(currentInflation, 2.0);

  // Project revenues over 15 years
  const baseRevenue = sponsorInput.grossMonthlyRent *
                      (sponsorInput.grossFacilityPower / sponsorInput.pue) *
                      1000 * 730;  // kW * hours/month

  const projectedRevenues = [];
  for (let year = 1; year <= 15; year++) {
    const yearRevenue = baseRevenue * Math.pow(1 + revenueEscalation / 100, year - 1);
    projectedRevenues.push({
      year: year,
      grossRevenue: yearRevenue,
      escalationRate: revenueEscalation
    });
  }

  return {
    baseRevenue: baseRevenue,
    escalationRate: revenueEscalation,
    projectedRevenues: projectedRevenues,
    inflationSource: `Eurostat HICP ${countryCode}`
  };
}
```

**New Metrics Enabled:**
- Country-specific inflation rates
- Construction cost indices
- Electricity price benchmarks
- GDP and unemployment data

---

### 6. Alpha Vantage API ⭐⭐⭐⭐

**Provider:** Alpha Vantage
**URL:** https://www.alphavantage.co/documentation/
**Cost:** Free tier: 25 requests/day (generous for daily updates)
**Rate Limit:** 25 requests/day, 5 requests/minute
**Update Frequency:** Real-time to daily depending on endpoint

#### Key Endpoints:

| Function | Description | Use Case |
|----------|-------------|----------|
| `FX_DAILY` | Daily FX rates | Currency conversion |
| `TREASURY_YIELD` | US Treasury yields | Risk-free rates |
| `INFLATION` | US CPI data | Inflation forecasting |
| `FEDERAL_FUNDS_RATE` | Fed funds rate | US base rate |
| `REAL_GDP` | US GDP growth | Economic indicator |

#### Implementation Example:

```javascript
class AlphaVantageClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = 'https://www.alphavantage.co/query';
    this.cache = new Map();
  }

  async getFXRate(fromCurrency, toCurrency) {
    const cacheKey = `fx_${fromCurrency}_${toCurrency}`;
    if (this.isCached(cacheKey)) {
      return this.cache.get(cacheKey).value;
    }

    const params = new URLSearchParams({
      function: 'FX_DAILY',
      from_symbol: fromCurrency,
      to_symbol: toCurrency,
      apikey: this.apiKey,
      outputsize: 'compact'
    });

    const response = await fetch(`${this.baseUrl}?${params}`);
    const data = await response.json();

    const timeSeries = data['Time Series FX (Daily)'];
    const latestDate = Object.keys(timeSeries)[0];
    const latestRate = parseFloat(timeSeries[latestDate]['4. close']);

    this.cache.set(cacheKey, { value: latestRate, timestamp: Date.now() });
    return latestRate;
  }

  async getTreasuryYield(maturity = '10year') {
    const params = new URLSearchParams({
      function: 'TREASURY_YIELD',
      interval: 'monthly',
      maturity: maturity,
      apikey: this.apiKey
    });

    const response = await fetch(`${this.baseUrl}?${params}`);
    const data = await response.json();

    const latestData = data.data[0];
    return parseFloat(latestData.value);
  }

  async getInflationRate() {
    const params = new URLSearchParams({
      function: 'INFLATION',
      apikey: this.apiKey
    });

    const response = await fetch(`${this.baseUrl}?${params}`);
    const data = await response.json();

    const latestData = data.data[0];
    return parseFloat(latestData.value);
  }

  isCached(key) {
    const cached = this.cache.get(key);
    if (!cached) return false;
    return (Date.now() - cached.timestamp) < 24 * 60 * 60 * 1000;
  }
}
```

**New Metrics Enabled:**
- Daily FX rates for major currencies
- US Treasury yield curve
- US inflation data
- Federal funds rate

---

### 7. World Bank API ⭐⭐⭐⭐

**Provider:** The World Bank Group
**URL:** https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
**Cost:** 100% Free, no API key required
**Rate Limit:** None specified
**Update Frequency:** Annual/Quarterly depending on indicator

#### Key Indicators:

| Indicator Code | Description | Use Case |
|----------------|-------------|----------|
| `FP.CPI.TOTL.ZG` | Inflation, consumer prices (annual %) | Country inflation |
| `NY.GDP.MKTP.KD.ZG` | GDP growth (annual %) | Economic health |
| `SL.UEM.TOTL.NE.ZS` | Unemployment rate | Labor market |
| `EG.ELC.ACCS.ZS` | Access to electricity (% of population) | Grid reliability proxy |
| `IC.BUS.EASE.XQ` | Ease of Doing Business score | Country risk |
| `GC.DOD.TOTL.GD.ZS` | Central government debt (% GDP) | Sovereign risk |

#### Implementation Example:

```javascript
class WorldBankClient {
  constructor() {
    this.baseUrl = 'https://api.worldbank.org/v2';
    this.cache = new Map();
  }

  async getIndicator(indicatorCode, countryCode) {
    const cacheKey = `${indicatorCode}_${countryCode}`;
    if (this.isCached(cacheKey)) {
      return this.cache.get(cacheKey).value;
    }

    const url = `${this.baseUrl}/country/${countryCode}/indicator/${indicatorCode}`;
    const params = new URLSearchParams({
      format: 'json',
      per_page: 1,
      date: `${new Date().getFullYear() - 1}:${new Date().getFullYear()}`
    });

    const response = await fetch(`${url}?${params}`);
    const data = await response.json();

    if (!data[1] || data[1].length === 0) {
      throw new Error(`No data available for ${indicatorCode} in ${countryCode}`);
    }

    const latestValue = parseFloat(data[1][0].value);
    this.cache.set(cacheKey, { value: latestValue, timestamp: Date.now() });

    return latestValue;
  }

  async getCountryInflation(countryCode) {
    return await this.getIndicator('FP.CPI.TOTL.ZG', countryCode);
  }

  async getGDPGrowth(countryCode) {
    return await this.getIndicator('NY.GDP.MKTP.KD.ZG', countryCode);
  }

  async getUnemploymentRate(countryCode) {
    return await this.getIndicator('SL.UEM.TOTL.NE.ZS', countryCode);
  }

  async getCountryRiskScore(countryCode) {
    // Composite risk score based on multiple indicators
    const gdpGrowth = await this.getGDPGrowth(countryCode);
    const debtToGDP = await this.getIndicator('GC.DOD.TOTL.GD.ZS', countryCode);
    const unemployment = await this.getUnemploymentRate(countryCode);

    // Simple risk scoring (0-100, lower = less risk)
    const riskScore = Math.min(100,
      (debtToGDP / 2) +           // Debt contributes up to 50 points
      (unemployment * 2) +         // Unemployment contributes up to 30 points
      Math.max(0, -gdpGrowth * 5)  // Negative growth contributes up to 20 points
    );

    return {
      score: riskScore,
      gdpGrowth: gdpGrowth,
      debtToGDP: debtToGDP,
      unemployment: unemployment,
      category: riskScore < 30 ? 'Low' : riskScore < 60 ? 'Medium' : 'High'
    };
  }

  isCached(key) {
    const cached = this.cache.get(key);
    if (!cached) return false;
    return (Date.now() - cached.timestamp) < 7 * 24 * 60 * 60 * 1000;  // 7 days
  }
}
```

#### Permutation Engine Integration:

```javascript
async function assessCountryRisk(sponsorInput) {
  const wb = new WorldBankClient();

  const countryCode = this.getISO3Code(sponsorInput.locationCountry);

  const riskAssessment = await wb.getCountryRiskScore(countryCode);
  const inflation = await wb.getCountryInflation(countryCode);

  // Adjust credit spreads based on country risk
  let countryRiskPremium = 0;  // bps
  if (riskAssessment.category === 'High') {
    countryRiskPremium = 100;  // +100bps for high-risk countries
  } else if (riskAssessment.category === 'Medium') {
    countryRiskPremium = 50;   // +50bps for medium-risk
  }

  return {
    countryCode: countryCode,
    countryName: sponsorInput.locationCountry,
    riskScore: riskAssessment.score,
    riskCategory: riskAssessment.category,
    riskPremium: countryRiskPremium,
    inflation: inflation,
    gdpGrowth: riskAssessment.gdpGrowth,
    unemployment: riskAssessment.unemployment,
    debtToGDP: riskAssessment.debtToGDP
  };
}
```

**New Metrics Enabled:**
- Country-specific inflation rates (200+ countries)
- GDP growth rates
- Sovereign risk indicators
- Country risk premium adjustment

---

### 8. Bank of England API ⭐⭐⭐⭐

**Provider:** Bank of England
**URL:** https://www.bankofengland.co.uk/boeapps/database/help.asp?Back=Y&Highlight=api
**Cost:** 100% Free, no API key required
**Rate Limit:** None specified
**Update Frequency:** Daily for rates, monthly for other series

#### Key Series:

| Series Code | Description | Use Case |
|-------------|-------------|----------|
| `IUDSOIA` | SONIA (Sterling Overnight Index Average) | GBP base rate |
| `IUDBEDR` | Bank Rate (Official Bank Rate) | UK policy rate |
| `IUDMNZC` | UK Gilt Yields (various maturities) | GBP risk-free curve |
| `XUQPIDQ` | UK CPI (12-month rate) | UK inflation |

#### Implementation Example:

```javascript
class BankOfEnglandClient {
  constructor() {
    this.baseUrl = 'https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp';
    this.cache = new Map();
  }

  async getSeries(seriesCode) {
    const cacheKey = seriesCode;
    if (this.isCached(cacheKey)) {
      return this.cache.get(cacheKey).value;
    }

    const params = new URLSearchParams({
      CodeVer: seriesCode,
      UsingCodes: 'Y',
      VPD: 'Y',
      VFD: 'N',
      xml: 'Y'
    });

    const response = await fetch(`${this.baseUrl}?${params}`);
    const xmlText = await response.text();

    // Parse XML (simplified)
    const latestValue = this.parseLatestValue(xmlText);

    this.cache.set(cacheKey, { value: latestValue, timestamp: Date.now() });
    return latestValue;
  }

  async getSONIA() {
    return await this.getSeries('IUDSOIA');
  }

  async getBankRate() {
    return await this.getSeries('IUDBEDR');
  }

  async getGiltYield(maturity = '10Y') {
    const maturityMap = {
      '5Y': 'IUDMNZC5',
      '10Y': 'IUDMNZC10',
      '20Y': 'IUDMNZC20'
    };
    return await this.getSeries(maturityMap[maturity]);
  }

  parseLatestValue(xmlText) {
    // Simplified XML parsing
    const regex = /<Obs OBS_VALUE="([\d.]+)"/;
    const match = xmlText.match(regex);
    return match ? parseFloat(match[1]) : null;
  }

  isCached(key) {
    const cached = this.cache.get(key);
    if (!cached) return false;
    return (Date.now() - cached.timestamp) < 6 * 60 * 60 * 1000;
  }
}
```

**New Metrics Enabled:**
- SONIA rates for GBP floating debt
- UK gilt yields
- Bank of England policy rate

---

### 9. IMF Data API (International Monetary Fund) ⭐⭐⭐

**Provider:** International Monetary Fund
**URL:** https://datahelp.imf.org/knowledgebase/articles/667681-using-json-restful-web-service
**Cost:** 100% Free, no API key required
**Rate Limit:** None specified
**Update Frequency:** Quarterly/Annual

#### Key Datasets:

| Database | Indicators | Use Case |
|----------|------------|----------|
| `IFS` (International Financial Statistics) | Interest rates, exchange rates, prices | Macro data |
| `WEO` (World Economic Outlook) | GDP, inflation, fiscal balance | Economic forecasting |
| `FSI` (Financial Soundness Indicators) | Bank capital, NPLs | Financial stability |

#### Implementation Example:

```javascript
class IMFClient {
  constructor() {
    this.baseUrl = 'https://www.imf.org/external/datamapper/api/v1';
    this.cache = new Map();
  }

  async getIndicator(indicator, countryCode) {
    const cacheKey = `${indicator}_${countryCode}`;
    if (this.isCached(cacheKey)) {
      return this.cache.get(cacheKey).value;
    }

    const url = `${this.baseUrl}/${indicator}`;
    const response = await fetch(url);
    const data = await response.json();

    const countryData = data.values[indicator][countryCode];
    const latestYear = Math.max(...Object.keys(countryData).map(Number));
    const latestValue = parseFloat(countryData[latestYear]);

    this.cache.set(cacheKey, { value: latestValue, timestamp: Date.now() });
    return latestValue;
  }

  async getGDPGrowth(countryCode) {
    return await this.getIndicator('NGDP_RPCH', countryCode);  // Real GDP growth
  }

  async getInflation(countryCode) {
    return await this.getIndicator('PCPIPCH', countryCode);  // CPI inflation
  }

  isCached(key) {
    const cached = this.cache.get(key);
    if (!cached) return false;
    return (Date.now() - cached.timestamp) < 7 * 24 * 60 * 60 * 1000;
  }
}
```

**New Metrics Enabled:**
- IMF GDP forecasts
- Inflation projections
- Financial stability indicators

---

### 10. OECD Data API ⭐⭐⭐

**Provider:** Organisation for Economic Co-operation and Development
**URL:** https://data.oecd.org/api/
**Cost:** 100% Free, no API key required
**Rate Limit:** None specified
**Update Frequency:** Quarterly/Annual

#### Key Datasets:

| Dataset | Description | Use Case |
|---------|-------------|----------|
| `CPI` | Consumer Price Index | Inflation |
| `GDP` | Gross Domestic Product | Economic growth |
| `LFS` | Labour Force Statistics | Unemployment |
| `EO` | Economic Outlook | Forecasts |

#### Implementation Example:

```javascript
class OECDClient {
  constructor() {
    this.baseUrl = 'https://stats.oecd.org/SDMX-JSON/data';
    this.cache = new Map();
  }

  async getDataset(dataset, country, measure = 'TOT') {
    const cacheKey = `${dataset}_${country}_${measure}`;
    if (this.isCached(cacheKey)) {
      return this.cache.get(cacheKey).value;
    }

    const url = `${this.baseUrl}/${dataset}/${country}.${measure}.A/all`;
    const params = new URLSearchParams({
      contentType: 'json'
    });

    const response = await fetch(`${url}?${params}`);
    const data = await response.json();

    // Parse SDMX-JSON structure
    const observations = data.dataSets[0].series['0:0:0'].observations;
    const latestIndex = Object.keys(observations).sort().pop();
    const latestValue = parseFloat(observations[latestIndex][0]);

    this.cache.set(cacheKey, { value: latestValue, timestamp: Date.now() });
    return latestValue;
  }

  async getInflation(countryCode) {
    return await this.getDataset('CPI', countryCode);
  }

  isCached(key) {
    const cached = this.cache.get(key);
    if (!cached) return false;
    return (Date.now() - cached.timestamp) < 7 * 24 * 60 * 60 * 1000;
  }
}
```

**New Metrics Enabled:**
- OECD inflation data
- GDP statistics
- Labor market data

---

### 11. CoinGecko API (for crypto-backed projects) ⭐⭐⭐

**Provider:** CoinGecko
**URL:** https://www.coingecko.com/en/api/documentation
**Cost:** Free tier: 10-50 calls/minute
**Rate Limit:** 10-50 calls/minute depending on plan
**Update Frequency:** Real-time

#### Use Case:
For data centers with crypto mining operations or crypto-backed revenue streams.

#### Implementation Example:

```javascript
class CoinGeckoClient {
  constructor() {
    this.baseUrl = 'https://api.coingecko.com/api/v3';
    this.cache = new Map();
  }

  async getCryptoPrice(coinId, vsCurrency = 'eur') {
    const cacheKey = `${coinId}_${vsCurrency}`;
    if (this.isCached(cacheKey)) {
      return this.cache.get(cacheKey).value;
    }

    const url = `${this.baseUrl}/simple/price`;
    const params = new URLSearchParams({
      ids: coinId,
      vs_currencies: vsCurrency
    });

    const response = await fetch(`${url}?${params}`);
    const data = await response.json();

    const price = data[coinId][vsCurrency];
    this.cache.set(cacheKey, { value: price, timestamp: Date.now() });

    return price;
  }

  isCached(key) {
    const cached = this.cache.get(key);
    if (!cached) return false;
    return (Date.now() - cached.timestamp) < 5 * 60 * 1000;  // 5 minutes
  }
}
```

**New Metrics Enabled:**
- Crypto price tracking for mining revenue
- Stablecoin valuations

---

### 12. US Census Bureau Economic Indicators API ⭐⭐⭐

**Provider:** US Census Bureau
**URL:** https://www.census.gov/data/developers/data-sets.html
**Cost:** 100% Free, requires API key
**Rate Limit:** 500 requests/day
**Update Frequency:** Monthly/Quarterly

#### Key Datasets:

| Dataset | Description | Use Case |
|---------|-------------|----------|
| Construction Spending | Private construction spending | CapEx benchmarking |
| Building Permits | New construction permits | Market supply |
| Retail Trade | Consumer spending | Economic health |

#### Implementation Example:

```javascript
class USCensusClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = 'https://api.census.gov/data';
    this.cache = new Map();
  }

  async getConstructionSpending(year, month) {
    const cacheKey = `construction_${year}_${month}`;
    if (this.isCached(cacheKey)) {
      return this.cache.get(cacheKey).value;
    }

    const url = `${this.baseUrl}/${year}/construction`;
    const params = new URLSearchParams({
      get: 'cell_value',
      for: 'us:*',
      time: `${year}-${month.toString().padStart(2, '0')}`,
      key: this.apiKey
    });

    const response = await fetch(`${url}?${params}`);
    const data = await response.json();

    const value = parseFloat(data[1][0]);
    this.cache.set(cacheKey, { value: value, timestamp: Date.now() });

    return value;
  }

  isCached(key) {
    const cached = this.cache.get(key);
    if (!cached) return false;
    return (Date.now() - cached.timestamp) < 30 * 24 * 60 * 60 * 1000;  // 30 days
  }
}
```

**New Metrics Enabled:**
- US construction spending trends
- Building permit data
- Market supply indicators

---

### 13. European DataWarehouse (EDW) API ⭐⭐⭐⭐

**Provider:** European DataWarehouse (ED)
**URL:** https://www.eurodw.eu/data-access
**Cost:** Free registration required, data access free
**Rate Limit:** Varies by registration level
**Update Frequency:** Monthly loan-level data

#### Use Case:
Access to actual European ABS loan-level data for benchmarking.

#### Key Data:
- ABS loan performance by sector
- Delinquency rates
- Prepayment speeds
- Loss severities

#### Implementation:

```javascript
class EDWClient {
  constructor(username, password) {
    this.username = username;
    this.password = password;
    this.baseUrl = 'https://www.eurodw.eu/api/v1';
    this.token = null;
  }

  async authenticate() {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: this.username,
        password: this.password
      })
    });

    const data = await response.json();
    this.token = data.token;
  }

  async getABSPerformanceData(sector, rating) {
    if (!this.token) await this.authenticate();

    const response = await fetch(`${this.baseUrl}/performance`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      method: 'POST',
      body: JSON.stringify({
        sector: sector,
        rating: rating,
        period: 'latest'
      })
    });

    const data = await response.json();
    return data;
  }
}
```

**New Metrics Enabled:**
- Real ABS delinquency benchmarks
- Sector-specific performance data
- Loss rate estimates

---

### 14. Climate Trace API ⭐⭐⭐

**Provider:** Climate TRACE (Tracking Real-time Atmospheric Carbon Emissions)
**URL:** https://climatetrace.org/
**Cost:** Free, requires registration
**Rate Limit:** TBD (newly available)
**Update Frequency:** Annual with quarterly updates

#### Use Case:
Calculate carbon footprint of data center for ESG scoring.

#### Implementation Example:

```javascript
class ClimateTraceClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = 'https://api.climatetrace.org/v1';
    this.cache = new Map();
  }

  async getGridCarbonIntensity(country, region) {
    const cacheKey = `carbon_${country}_${region}`;
    if (this.isCached(cacheKey)) {
      return this.cache.get(cacheKey).value;
    }

    const response = await fetch(`${this.baseUrl}/electricity/intensity`, {
      headers: { 'Authorization': `Bearer ${this.apiKey}` },
      method: 'GET',
      params: {
        country: country,
        region: region
      }
    });

    const data = await response.json();
    const intensity = data.carbon_intensity_gco2_per_kwh;

    this.cache.set(cacheKey, { value: intensity, timestamp: Date.now() });
    return intensity;
  }

  async calculateDataCenterCarbon(itLoadMW, pue, country, region) {
    const carbonIntensity = await this.getGridCarbonIntensity(country, region);

    const totalPowerMW = itLoadMW * pue;
    const annualMWh = totalPowerMW * 8760;
    const annualCO2Tonnes = (annualMWh * 1000 * carbonIntensity) / 1000000;

    return {
      annualCO2Tonnes: annualCO2Tonnes,
      carbonIntensity: carbonIntensity,
      powerConsumption: annualMWh,
      esgCategory: annualCO2Tonnes < 10000 ? 'Low' : annualCO2Tonnes < 50000 ? 'Medium' : 'High'
    };
  }

  isCached(key) {
    const cached = this.cache.get(key);
    if (!cached) return false;
    return (Date.now() - cached.timestamp) < 90 * 24 * 60 * 60 * 1000;  // 90 days
  }
}
```

**New Metrics Enabled:**
- Grid carbon intensity by region
- Data center carbon footprint
- ESG scoring based on emissions

---

### 15. OpenWeatherMap API ⭐⭐⭐

**Provider:** OpenWeatherMap
**URL:** https://openweathermap.org/api
**Cost:** Free tier: 1,000 calls/day
**Rate Limit:** 60 calls/minute
**Update Frequency:** Real-time

#### Use Case:
Temperature data for cooling OPEX estimation.

#### Implementation Example:

```javascript
class OpenWeatherMapClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = 'https://api.openweathermap.org/data/3.0';
    this.cache = new Map();
  }

  async getHistoricalTemperature(lat, lon, startDate, endDate) {
    const cacheKey = `temp_${lat}_${lon}_${startDate}`;
    if (this.isCached(cacheKey)) {
      return this.cache.get(cacheKey).value;
    }

    const url = `${this.baseUrl}/onecall/timemachine`;
    const params = new URLSearchParams({
      lat: lat,
      lon: lon,
      dt: Math.floor(startDate.getTime() / 1000),
      appid: this.apiKey,
      units: 'metric'
    });

    const response = await fetch(`${url}?${params}`);
    const data = await response.json();

    const avgTemp = data.hourly.reduce((sum, h) => sum + h.temp, 0) / data.hourly.length;

    this.cache.set(cacheKey, { value: avgTemp, timestamp: Date.now() });
    return avgTemp;
  }

  async calculateCoolingLoad(lat, lon, itLoadMW) {
    const today = new Date();
    const yearAgo = new Date(today.getTime() - 365 * 24 * 60 * 60 * 1000);

    const avgTemp = await this.getHistoricalTemperature(lat, lon, yearAgo, today);

    // Simplified cooling load calculation
    // COP (Coefficient of Performance) degrades with ambient temperature
    const baseCOP = 3.5;  // Modern data center chillers
    const tempDegradation = (avgTemp - 15) * 0.02;  // 2% degradation per °C above 15°C
    const effectiveCOP = baseCOP - tempDegradation;

    const coolingPowerMW = itLoadMW / effectiveCOP;

    return {
      avgTemperature: avgTemp,
      effectiveCOP: effectiveCOP,
      coolingLoadMW: coolingPowerMW,
      totalOverhead: coolingPowerMW / itLoadMW
    };
  }

  isCached(key) {
    const cached = this.cache.get(key);
    if (!cached) return false;
    return (Date.now() - cached.timestamp) < 30 * 24 * 60 * 60 * 1000;  // 30 days
  }
}
```

**New Metrics Enabled:**
- Location-specific cooling requirements
- Temperature-adjusted PUE
- Climate-based OPEX adjustments

---

### 16. Quandl/Nasdaq Data Link API ⭐⭐⭐

**Provider:** Nasdaq Data Link (formerly Quandl)
**URL:** https://data.nasdaq.com/tools/api
**Cost:** Free tier available (limited datasets)
**Rate Limit:** 50 calls/day (free tier)
**Update Frequency:** Varies by dataset

#### Key Datasets (Free):

| Dataset | Description | Use Case |
|---------|-------------|----------|
| `FRED/*` | Federal Reserve Economic Data | Rates, inflation |
| `ZILLOW/*` | Real estate price indices | Land valuation |
| `WIKI/*` | Stock prices | Public comps |

#### Implementation Example:

```javascript
class QuandlClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = 'https://data.nasdaq.com/api/v3';
    this.cache = new Map();
  }

  async getDataset(databaseCode, datasetCode) {
    const cacheKey = `${databaseCode}_${datasetCode}`;
    if (this.isCached(cacheKey)) {
      return this.cache.get(cacheKey).value;
    }

    const url = `${this.baseUrl}/datasets/${databaseCode}/${datasetCode}/data.json`;
    const params = new URLSearchParams({
      api_key: this.apiKey,
      limit: 1,
      order: 'desc'
    });

    const response = await fetch(`${url}?${params}`);
    const data = await response.json();

    const latestValue = data.dataset_data.data[0][1];
    this.cache.set(cacheKey, { value: latestValue, timestamp: Date.now() });

    return latestValue;
  }

  isCached(key) {
    const cached = this.cache.get(key);
    if (!cached) return false;
    return (Date.now() - cached.timestamp) < 24 * 60 * 60 * 1000;
  }
}
```

**New Metrics Enabled:**
- Alternative economic data
- Real estate price indices
- Commodity prices

---

### 17. Carbon Intensity API ⭐⭐⭐

**Provider:** National Grid ESO (UK), various European TSOs
**URL:** https://carbonintensity.org.uk/ (UK), https://www.electricitymap.org/
**Cost:** 100% Free
**Rate Limit:** None specified
**Update Frequency:** Every 30 minutes

#### Implementation Example:

```javascript
class CarbonIntensityClient {
  constructor() {
    this.baseUrl = 'https://api.carbonintensity.org.uk';
    this.cache = new Map();
  }

  async getCurrentIntensity(postcode = null) {
    const cacheKey = `intensity_${postcode || 'national'}`;
    if (this.isCached(cacheKey)) {
      return this.cache.get(cacheKey).value;
    }

    let url = `${this.baseUrl}/intensity`;
    if (postcode) {
      url = `${this.baseUrl}/regional/postcode/${postcode}`;
    }

    const response = await fetch(url);
    const data = await response.json();

    const intensity = postcode ?
      data.data[0].data[0].intensity.forecast :
      data.data[0].intensity.forecast;

    this.cache.set(cacheKey, { value: intensity, timestamp: Date.now() });
    return intensity;
  }

  async calculateGreenBondEligibility(itLoadMW, pue, postcode) {
    const carbonIntensity = await this.getCurrentIntensity(postcode);

    const totalPowerMW = itLoadMW * pue;
    const annualCO2Tonnes = totalPowerMW * 8760 * carbonIntensity / 1000000;

    // EU Taxonomy threshold for data centers
    const euTaxonomyThreshold = 50000;  // tonnes CO2e/year

    const eligible = annualCO2Tonnes < euTaxonomyThreshold;

    return {
      carbonIntensity: carbonIntensity,
      annualCO2Tonnes: annualCO2Tonnes,
      euTaxonomyEligible: eligible,
      greenBondPremium: eligible ? -15 : 0  // -15bps if eligible
    };
  }

  isCached(key) {
    const cached = this.cache.get(key);
    if (!cached) return false;
    return (Date.now() - cached.timestamp) < 30 * 60 * 1000;  // 30 minutes
  }
}
```

**New Metrics Enabled:**
- Real-time grid carbon intensity
- Green bond eligibility
- ESG premium/discount calculation

---

### 18. REST Countries API ⭐⭐⭐

**Provider:** REST Countries
**URL:** https://restcountries.com/
**Cost:** 100% Free
**Rate Limit:** None
**Update Frequency:** Static (country reference data)

#### Use Case:
Country metadata for risk scoring, currency codes, regional grouping.

#### Implementation Example:

```javascript
class RESTCountriesClient {
  constructor() {
    this.baseUrl = 'https://restcountries.com/v3.1';
    this.cache = new Map();
  }

  async getCountryData(countryName) {
    const cacheKey = countryName;
    if (this.isCached(cacheKey)) {
      return this.cache.get(cacheKey).value;
    }

    const url = `${this.baseUrl}/name/${countryName}`;
    const response = await fetch(url);
    const data = await response.json();

    const country = data[0];
    const metadata = {
      name: country.name.common,
      code: country.cca3,
      currency: Object.keys(country.currencies)[0],
      region: country.region,
      subregion: country.subregion,
      population: country.population,
      area: country.area,
      timezones: country.timezones
    };

    this.cache.set(cacheKey, { value: metadata, timestamp: Date.now() });
    return metadata;
  }

  isCached(key) {
    const cached = this.cache.get(key);
    if (!cached) return false;
    return (Date.now() - cached.timestamp) < 30 * 24 * 60 * 60 * 1000;  // 30 days
  }
}
```

**New Metrics Enabled:**
- Automatic currency code detection
- Regional grouping for benchmarking
- Country metadata enrichment

---

### 19. Open Street Map Nominatim API ⭐⭐⭐

**Provider:** OpenStreetMap Foundation
**URL:** https://nominatim.org/release-docs/develop/api/Overview/
**Cost:** 100% Free
**Rate Limit:** 1 request/second
**Update Frequency:** Real-time

#### Use Case:
Geocoding for location coordinates (needed for weather, distance calculations).

#### Implementation Example:

```javascript
class NominatimClient {
  constructor() {
    this.baseUrl = 'https://nominatim.openstreetmap.org';
    this.cache = new Map();
  }

  async geocode(address) {
    const cacheKey = address;
    if (this.isCached(cacheKey)) {
      return this.cache.get(cacheKey).value;
    }

    // Rate limiting: 1 request/second
    await this.rateLimit();

    const url = `${this.baseUrl}/search`;
    const params = new URLSearchParams({
      q: address,
      format: 'json',
      limit: 1
    });

    const response = await fetch(`${url}?${params}`, {
      headers: {
        'User-Agent': 'AtlasNexusABSCalculator/1.0'
      }
    });

    const data = await response.json();

    if (data.length === 0) {
      throw new Error(`Location not found: ${address}`);
    }

    const location = {
      lat: parseFloat(data[0].lat),
      lon: parseFloat(data[0].lon),
      displayName: data[0].display_name
    };

    this.cache.set(cacheKey, { value: location, timestamp: Date.now() });
    return location;
  }

  async rateLimit() {
    // Ensure 1 second between requests
    const now = Date.now();
    if (this.lastRequest && (now - this.lastRequest) < 1000) {
      await new Promise(resolve => setTimeout(resolve, 1000 - (now - this.lastRequest)));
    }
    this.lastRequest = Date.now();
  }

  isCached(key) {
    const cached = this.cache.get(key);
    if (!cached) return false;
    return (Date.now() - cached.timestamp) < 90 * 24 * 60 * 60 * 1000;  // 90 days
  }
}
```

**New Metrics Enabled:**
- Geocoding for weather API integration
- Distance calculations
- Location validation

---

### 20. IP Geolocation API (ipapi.co) ⭐⭐

**Provider:** ipapi.co
**URL:** https://ipapi.co/api/
**Cost:** Free tier: 1,000 requests/day
**Rate Limit:** 1,000 requests/day
**Update Frequency:** Real-time

#### Use Case:
Auto-detect user location for default currency and country settings.

#### Implementation Example:

```javascript
class IPGeolocationClient {
  constructor() {
    this.baseUrl = 'https://ipapi.co';
  }

  async getCurrentLocation() {
    const response = await fetch(`${this.baseUrl}/json/`);
    const data = await response.json();

    return {
      country: data.country_name,
      countryCode: data.country_code,
      currency: data.currency,
      region: data.region,
      city: data.city,
      timezone: data.timezone
    };
  }

  async suggestDefaults() {
    const location = await this.getCurrentLocation();

    return {
      locationCountry: location.country,
      capexCurrency: location.currency,
      kwhCurrency: location.currency,
      timezone: location.timezone
    };
  }
}
```

**New Metrics Enabled:**
- Auto-populate location defaults
- User experience enhancement

---

## Implementation Architecture

### Central API Manager

```javascript
class LiveDataAPIManager {
  constructor(config) {
    this.clients = {
      fred: new FREDClient(config.fredApiKey),
      ecb: new ECBClient(),
      fx: new OpenExchangeRatesClient(config.fxApiKey),
      entsoe: new ENTSOEClient(config.entsoeToken),
      eurostat: new EurostatClient(),
      alphaVantage: new AlphaVantageClient(config.alphaVantageKey),
      worldBank: new WorldBankClient(),
      boe: new BankOfEnglandClient(),
      imf: new IMFClient(),
      oecd: new OECDClient(),
      coingecko: new CoinGeckoClient(),
      census: new USCensusClient(config.censusKey),
      edw: new EDWClient(config.edwUsername, config.edwPassword),
      climate: new ClimateTraceClient(config.climateTraceKey),
      weather: new OpenWeatherMapClient(config.weatherKey),
      quandl: new QuandlClient(config.quandlKey),
      carbon: new CarbonIntensityClient(),
      countries: new RESTCountriesClient(),
      geocode: new NominatimClient(),
      ipgeo: new IPGeolocationClient()
    };

    this.fallbackStrategies = new Map();
    this.setupFallbacks();
  }

  setupFallbacks() {
    // EURIBOR fallback chain: ECB -> FRED -> Static
    this.fallbackStrategies.set('euribor', [
      () => this.clients.ecb.getEURIBOR('6M'),
      () => this.clients.fred.getSeries('IR3TIB01EZM156N'),  // EURIBOR 3M from FRED
      () => 3.5  // Static fallback
    ]);

    // FX fallback chain: OpenExchangeRates -> ECB -> FRED -> Static
    this.fallbackStrategies.set('fxrate', [
      (from, to) => this.clients.fx.convertCurrency(1, from, to).then(r => r.rate),
      (from, to) => this.clients.ecb.getFXRate(from),
      (from, to) => this.clients.fred.getSeries(`DEXUS${to}`),
      (from, to) => 1.0  // Static fallback
    ]);
  }

  async getWithFallback(strategyKey, ...args) {
    const strategies = this.fallbackStrategies.get(strategyKey);

    for (const strategy of strategies) {
      try {
        const result = await strategy(...args);
        if (result !== null && result !== undefined) {
          return result;
        }
      } catch (error) {
        console.warn(`Fallback strategy failed: ${error.message}`);
        continue;
      }
    }

    throw new Error(`All fallback strategies failed for ${strategyKey}`);
  }

  async enhancePermutationInput(sponsorInput) {
    // Gather all live data in parallel
    const [
      seniorPricing,
      inflation,
      fxRates,
      countryRisk,
      electricityOPEX,
      carbonData
    ] = await Promise.all([
      this.getSeniorDebtPricing(sponsorInput),
      this.getInflationData(sponsorInput),
      this.getFXRates(sponsorInput),
      this.getCountryRisk(sponsorInput),
      this.getElectricityOPEX(sponsorInput),
      this.getCarbonData(sponsorInput)
    ]);

    return {
      ...sponsorInput,
      liveData: {
        seniorPricing,
        inflation,
        fxRates,
        countryRisk,
        electricityOPEX,
        carbonData
      },
      timestamp: new Date().toISOString()
    };
  }

  async getSeniorDebtPricing(sponsorInput) {
    const currency = sponsorInput.capexCurrency;

    let baseRate, creditSpread;

    if (currency === 'EUR') {
      baseRate = await this.getWithFallback('euribor');
      creditSpread = await this.getEuroCreditSpread(sponsorInput.targetRating);
    } else if (currency === 'USD') {
      baseRate = await this.clients.fred.getSOFR();
      creditSpread = await this.clients.fred.getCreditSpread(sponsorInput.targetRating);
    } else if (currency === 'GBP') {
      baseRate = await this.clients.boe.getSONIA();
      creditSpread = await this.getGBPCreditSpread(sponsorInput.targetRating);
    }

    const sectorPremium = 25;  // bps for data centers
    const countryRisk = await this.getCountryRiskPremium(sponsorInput.locationCountry);

    const allInCoupon = baseRate + (creditSpread + sectorPremium + countryRisk) / 100;

    return {
      baseRate,
      creditSpread,
      sectorPremium,
      countryRiskPremium: countryRisk,
      allInCoupon
    };
  }

  async getInflationData(sponsorInput) {
    const countryCode = this.getCountryCode(sponsorInput.locationCountry);

    let inflation;
    try {
      inflation = await this.clients.worldBank.getCountryInflation(countryCode);
    } catch {
      inflation = await this.clients.eurostat.getInflationRate(countryCode);
    }

    const revenueEscalation = Math.max(inflation, 2.0);  // 2% floor

    return {
      currentInflation: inflation,
      revenueEscalation,
      source: 'World Bank / Eurostat'
    };
  }

  async getFXRates(sponsorInput) {
    const baseCurrency = 'EUR';
    const currencies = ['USD', 'GBP', 'JPY', 'AED'];

    const rates = {};
    for (const currency of currencies) {
      if (currency === baseCurrency) {
        rates[currency] = 1.0;
      } else {
        rates[currency] = await this.getWithFallback('fxrate', currency, baseCurrency);
      }
    }

    return rates;
  }

  async getCountryRisk(sponsorInput) {
    const countryCode = this.getCountryCode(sponsorInput.locationCountry);

    const wb = this.clients.worldBank;
    const riskData = await wb.getCountryRiskScore(countryCode);

    return riskData;
  }

  async getElectricityOPEX(sponsorInput) {
    if (sponsorInput.leaseType !== 'Gross') {
      return null;
    }

    const countryCode = this.getCountryCode(sponsorInput.locationCountry);

    let electricityPrice;
    try {
      electricityPrice = await this.clients.entsoe.getDayAheadPrices(countryCode, new Date(), new Date());
    } catch {
      electricityPrice = await this.clients.eurostat.getElectricityPrice(countryCode);
    }

    const itLoadMW = sponsorInput.grossFacilityPower / sponsorInput.pue;
    const annualMWh = itLoadMW * 8760;
    const annualCost = annualMWh * electricityPrice;

    return {
      pricePerMWh: electricityPrice,
      annualCost,
      source: 'ENTSO-E / Eurostat'
    };
  }

  async getCarbonData(sponsorInput) {
    const location = await this.clients.geocode.geocode(
      `${sponsorInput.locationCountry}, data center location`
    );

    const climate = this.clients.climate;
    const carbonData = await climate.calculateDataCenterCarbon(
      sponsorInput.grossFacilityPower / sponsorInput.pue,
      sponsorInput.pue,
      sponsorInput.locationCountry,
      location.displayName
    );

    // Green bond premium if low carbon
    const greenBondPremium = carbonData.esgCategory === 'Low' ? -15 : 0;  // -15bps

    return {
      ...carbonData,
      greenBondPremium
    };
  }

  getCountryCode(countryName) {
    const countryMap = {
      'United Kingdom': 'GB',
      'Germany': 'DE',
      'France': 'FR',
      'Ireland': 'IE',
      'Netherlands': 'NL',
      'Spain': 'ES',
      'Italy': 'IT',
      'Poland': 'PL',
      'Sweden': 'SE',
      'Norway': 'NO'
      // ... add all countries
    };
    return countryMap[countryName] || 'GB';
  }
}
```

---

## New Calculated Metrics Summary

### Total New Metrics: 150+

#### 1. **Interest Rate Risk Metrics** (15 metrics)
- Duration (Macaulay, Modified)
- DV01 (Dollar Value of 01)
- Convexity
- Key Rate Durations
- Effective Duration
- Spread Duration
- Interest Rate Stress Scenarios (+100bps, +200bps, +300bps)

#### 2. **Credit Risk Metrics** (12 metrics)
- Probability of Default (PD) by rating
- Loss Given Default (LGD) by tranche
- Expected Loss (PD × LGD × Exposure)
- Credit VaR (95%, 99%)
- Default Correlation
- Recovery Rate estimates
- Credit Spread Sensitivity
- Rating Migration Probability

#### 3. **Market Risk Metrics** (18 metrics)
- Value at Risk (VaR) - 1-day, 10-day at 95%, 99%
- Conditional VaR (CVaR)
- Stress Test Scenarios:
  - 2008 Financial Crisis
  - 2022 Energy Crisis
  - COVID-19 Recession
  - Sovereign Debt Crisis
  - Inflation Shock
  - Interest Rate Shock
- Volatility (historical, implied)
- Beta to market indices
- Correlation Matrix

#### 4. **FX Risk Metrics** (8 metrics)
- FX Exposure by currency
- FX VaR
- Unhedged FX Position
- FX Hedge Ratio
- FX Delta
- Cross-Currency Basis
- FX Stress Scenarios

#### 5. **Liquidity Metrics** (6 metrics)
- Bid-Ask Spread estimate
- Days to Liquidity
- Trading Volume estimate
- Market Depth
- Liquidity Score
- Secondary Market Price estimate

#### 6. **ESG Metrics** (15 metrics)
- Carbon Footprint (Scope 1, 2, 3)
- Grid Carbon Intensity
- Renewable Energy %
- PUE (actual vs. industry benchmark)
- Water Usage Effectiveness (WUE)
- Green Revenue %
- EU Taxonomy Alignment %
- Social Impact Score
- Governance Score
- ESG Composite Score
- Green Bond Eligibility
- Green Bond Premium/Discount
- Carbon Credits Value
- ESG Rating (predicted)
- TCFD Alignment

#### 7. **Country/Sovereign Risk Metrics** (10 metrics)
- Country Risk Score (0-100)
- Sovereign Credit Rating
- GDP Growth
- Inflation Rate
- Unemployment Rate
- Debt-to-GDP Ratio
- Political Stability Index
- Ease of Doing Business
- Currency Risk
- Country Risk Premium (bps)

#### 8. **Real-Time Pricing Metrics** (20 metrics)
- Live EURIBOR (1M, 3M, 6M, 12M)
- Live SOFR
- Live SONIA
- Live Treasury Yields (1Y, 3Y, 5Y, 7Y, 10Y)
- Live Credit Spreads (AAA, AA, A, BBB, BB, B)
- Live FX Rates (EUR/USD, EUR/GBP, EUR/JPY, EUR/AED)
- Live Electricity Prices
- Live Inflation Rates
- Live GDP Growth
- Dynamic WACC

#### 9. **Construction & CapEx Metrics** (8 metrics)
- Construction Cost Index
- Construction Inflation
- Material Price Indices (steel, concrete, copper)
- Labor Cost Index
- Supply Chain Risk Score
- Cost Overrun Probability
- Schedule Delay Probability
- CapEx Stress Scenarios

#### 10. **Revenue & OPEX Metrics** (12 metrics)
- Market Rent Benchmark
- Rent Premium/Discount %
- Occupancy Forecast
- Lease Rollover Schedule
- Re-leasing Probability
- Tenant Credit Quality Score
- Electricity Cost Forecast (15 years)
- OPEX Inflation Forecast
- Revenue at Risk
- OPEX Stress Scenarios
- Net Income Volatility
- DSCR Volatility

#### 11. **Debt Sizing & Structure Metrics** (10 metrics)
- Optimal Leverage Ratio
- LTV Sensitivity
- Debt Capacity
- DSCR Headroom
- Rating Threshold Distance
- Deleveraging Timeline
- Refinancing Risk Score
- Maturity Profile
- Tranche Subordination %
- Excess Spread

#### 12. **Equity Metrics** (8 metrics)
- Equity IRR (nominal, real)
- Equity Multiple
- Cash-on-Cash Return
- Equity NPV
- Equity Duration
- Equity Volatility
- Equity Downside Protection
- Equity Stress Returns

#### 13. **Comparative Metrics** (8 metrics)
- Comparable Deal Pricing
- Sector Median DSCR
- Sector Median LTV
- Sector Median Spreads
- Percentile Ranking
- Z-Score vs. Sector
- Relative Value Score
- Market Positioning

---

## API Key Management

### Environment Variables (.env)

```bash
# Interest Rates & Credit
FRED_API_KEY=your_fred_api_key_here

# FX Rates
OPEN_EXCHANGE_RATES_APP_ID=your_fx_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here

# Electricity
ENTSOE_SECURITY_TOKEN=your_entsoe_token_here

# Weather & Climate
OPENWEATHER_API_KEY=your_weather_api_key_here
CLIMATE_TRACE_API_KEY=your_climate_api_key_here

# Census & Economic
US_CENSUS_API_KEY=your_census_key_here

# ABS Data
EDW_USERNAME=your_edw_username_here
EDW_PASSWORD=your_edw_password_here

# Quandl
QUANDL_API_KEY=your_quandl_key_here
```

---

## Testing & Validation

```javascript
// API health check endpoint
async function checkAPIHealth() {
  const manager = new LiveDataAPIManager(process.env);

  const healthChecks = {
    fred: () => manager.clients.fred.getSOFR(),
    ecb: () => manager.clients.ecb.getEURIBOR('6M'),
    fx: () => manager.clients.fx.getLatestRates('EUR'),
    entsoe: () => manager.clients.entsoe.getDayAheadPrices('UK', new Date(), new Date()),
    eurostat: () => manager.clients.eurostat.getInflationRate('DE'),
    worldBank: () => manager.clients.worldBank.getCountryInflation('GBR'),
    carbon: () => manager.clients.carbon.getCurrentIntensity()
  };

  const results = {};

  for (const [api, check] of Object.entries(healthChecks)) {
    try {
      const startTime = Date.now();
      await check();
      const latency = Date.now() - startTime;
      results[api] = { status: 'OK', latency: `${latency}ms` };
    } catch (error) {
      results[api] = { status: 'FAILED', error: error.message };
    }
  }

  return results;
}
```

---

## Deployment Checklist

- [ ] Register for all API keys (FRED, ENTSO-E, etc.)
- [ ] Configure environment variables in production
- [ ] Set up API key rotation policy
- [ ] Implement caching strategy (Redis recommended)
- [ ] Set up monitoring for API failures
- [ ] Implement rate limiting on frontend
- [ ] Add fallback strategies for critical APIs
- [ ] Test all API integrations in staging
- [ ] Document API dependencies
- [ ] Set up alerts for API quota limits

---

## Cost Analysis (All Free Tiers)

| API | Free Tier Limit | Monthly Cost | Notes |
|-----|-----------------|--------------|-------|
| FRED | Unlimited | $0 | No limit |
| ECB | Unlimited | $0 | No limit |
| Open Exchange Rates | 1,000 req/mo | $0 | Sufficient for most cases |
| ENTSO-E | 400 req/min | $0 | No monthly limit |
| Eurostat | Unlimited | $0 | No limit |
| Alpha Vantage | 25 req/day | $0 | 750 req/mo |
| World Bank | Unlimited | $0 | No limit |
| Bank of England | Unlimited | $0 | No limit |
| IMF | Unlimited | $0 | No limit |
| OECD | Unlimited | $0 | No limit |
| CoinGecko | 10-50 req/min | $0 | Sufficient |
| US Census | 500 req/day | $0 | 15,000 req/mo |
| EDW | Registration required | $0 | Free after registration |
| Climate Trace | TBD | $0 | New API |
| OpenWeatherMap | 1,000 req/day | $0 | 30,000 req/mo |
| Quandl | 50 req/day | $0 | 1,500 req/mo |
| Carbon Intensity | Unlimited | $0 | No limit |
| REST Countries | Unlimited | $0 | Static data |
| Nominatim | 1 req/sec | $0 | ~2.6M req/mo |
| ipapi.co | 1,000 req/day | $0 | 30,000 req/mo |

**Total Monthly Cost: $0**

---

## Performance Impact

### Expected Latency per Permutation:

- Without Live Data: ~500ms
- With Live Data (cached): ~600ms (+100ms)
- With Live Data (uncached): ~2,500ms (+2,000ms)

### Mitigation Strategies:

1. **Aggressive Caching:** Cache API responses for 6-24 hours
2. **Pre-warming:** Fetch common data on server startup
3. **Parallel Requests:** Fetch all APIs simultaneously
4. **Lazy Loading:** Only fetch APIs needed for specific calculations
5. **Background Jobs:** Update cache in background every hour

---

**Last Updated:** 2026-01-19
**Status:** Planning Phase - Ready for Implementation
**Total APIs:** 20
**Total New Metrics:** 150+
**Total Cost:** $0/month
