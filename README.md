# SMC Toolkit + Free NEPSE GitHub Data System

यो package तपाईंको साथीको छुट्टै GitHub account मा राख्न तयार गरिएको हो। यसमा feature-rich SMC Toolkit, Google Sheet बाट seed गरिएको historical NEPSE data, yearly JSON chunks, ShareSansar scraper, र Monday–Friday GitHub Actions workflow समावेश छन्।

## Package मा के-के छ?

| File/folder | काम |
| --- | --- |
| `index.html` | Full feature-rich SMC Toolkit website। SMC Chart ले GitHub को `data/chunks/` पढ्छ। |
| `data/chunks/` | 2017–2026 को historical OHLC data yearly JSON files मा। |
| `data/chunks/manifest.json` | सबै yearly chunk files को list। |
| `data/latest.json`, `data/latest.csv` | पछिल्लो valid trading-day snapshot। |
| `data/nepse_ohlc_fast.json` | SMC Chart छिटो देखाउन index/sub-index history। |
| `data/nepse_ohlc.csv` | Full history को CSV copy। |
| `scripts/update_nepse.py` | ShareSansar को public pages बाट daily data fetch गर्ने Python script। |
| `scripts/data_chunks.py` | History लाई GitHub upload-friendly yearly chunks मा लेख्ने helper। |
| `.github/workflows/daily-nepse.yml` | Monday–Friday automatic GitHub Actions workflow। |
| `requirements.txt` | Python dependencies। |
| `tests/test_update_nepse.py` | Offline validation tests। |

> महत्वपूर्ण: `index.html` पहिले नै तयार छ। यसलाई `smc_toolkit_github_features.html` भनेर rename गर्नु पर्दैन। Repository root मा यसको नाम `index.html` नै रहनुपर्छ।

## Step 1: Friend को GitHub repository बनाउने

Friend ले आफ्नो GitHub account मा login गरेर **New repository** खोल्नुपर्छ। Repository को नाम ठ्याक्कै यस्तो हुनुपर्छ:

```text
FRIEND_USERNAME.github.io
```

उदाहरण: username `ram123` भए repository name:

```text
ram123.github.io
```

Repository **Public** राख्नुहोस्। `Add a README file` जस्ता विकल्पहरू सुरुमा select नगर्नु राम्रो हुन्छ। त्यसपछि **Create repository** थिच्नुहोस्।

यो project लाई user-site repository मा राख्नु आवश्यक छ, किनकि SMC iframe ले GitHub data लाई root path बाट पढ्छ।

## Step 2: GitHub Desktop बाट repository clone गर्ने

1. GitHub Desktop install गरेर friend को GitHub account बाट sign in गर्नुहोस्।
2. **File → Clone repository** खोल्नुहोस्।
3. Friend को `FRIEND_USERNAME.github.io` repository select गर्नुहोस्।
4. Local path छानेर **Clone** थिच्नुहोस्।
5. Clone भएको खाली folder खोल्नुहोस्।

## Step 3: Package का files copy गर्ने

1. यो ZIP file extract गर्नुहोस्।
2. Extract भएको `smc_nepse_friend_bundle` folder भित्रका सबै files र folders copy गर्नुहोस्।
3. ती files friend को cloned repository folder को root मा paste गर्नुहोस्।
4. यदि Windows ले hidden `.github` folder नदेखाएमा File Explorer मा **View → Show → Hidden items** enable गर्नुहोस्।
5. Repository root मा कम्तीमा यी items देखिनुपर्छ:

```text
index.html
 data/
 scripts/
 tests/
 requirements.txt
 .github/workflows/daily-nepse.yml
```

`data/chunks/manifest.json` र `data/chunks/2017.json` देखि `2026.json` सम्मका files छुट्नु हुँदैन।

## Step 4: GitHub Desktop बाट commit र push गर्ने

GitHub Desktop मा फर्केर:

1. Changes tab मा files देखिएपछि सबै changes select भएको पुष्टि गर्नुहोस्।
2. Summary मा लेख्नुहोस्: `Add SMC Toolkit and NEPSE GitHub data system`
3. **Commit to main** थिच्नुहोस्।
4. माथिको **Push origin** थिच्नुहोस्।

Data files ठूलो भएकाले browser को **Add file → Upload files** बाट upload नगर्नुहोस्। GitHub Desktop प्रयोग गर्नुहोस्।

## Step 5: GitHub Pages enable गर्ने

Friend को repository मा:

1. **Settings → Pages** खोल्नुहोस्।
2. **Build and deployment → Source** मा `Deploy from a branch` select गर्नुहोस्।
3. Branch मा `main` र folder मा `/ (root)` select गर्नुहोस्।
4. **Save** थिच्नुहोस्।

केही समयपछि website यस्तो URL मा खुल्छ:

```text
https://FRIEND_USERNAME.github.io/
```

## Step 6: GitHub Actions permission enable गर्ने

Repository मा:

1. **Settings → Actions → General** खोल्नुहोस्।
2. Workflow permissions मा **Read and write permissions** select गर्नुहोस्।
3. **Save** थिच्नुहोस्।
4. त्यसपछि **Actions → Daily NEPSE OHLC update → Run workflow → Run workflow** थिचेर manual test गर्नुहोस्।

Successful run भएमा workflow ले `data/` files मात्र update गर्छ। Source मा आजको valid trading date नभए workflow green/no-op हुन सक्छ; यस्तो अवस्थामा नयाँ commit नआउनु सही behavior हो।

## Daily update behavior

Workflow `12:30 UTC`, अर्थात् लगभग `18:15 Nepal time`, Monday–Friday मा चल्छ। Python script ले थप validation गर्छ:

| अवस्था | Result |
| --- | --- |
| Monday–Friday र ShareSansar मा आजकै date | Data update र commit हुन्छ। |
| Saturday/Sunday | No-op; कुनै नयाँ row हुँदैन। |
| Public holiday वा market बन्द | Source date पुरानो/missing भए no-op हुन्छ। |
| Invalid वा धेरै कम symbol data | Partial data publish हुँदैन। |
| एउटै date फेरि आयो | Duplicate row नबनी existing row merge हुन्छ। |

## महत्वपूर्ण Apps Script note

यो `index.html` full feature-rich version हो। यसमा **SMC Chart को data source मात्र GitHub chunks मा migrate गरिएको** छ। अन्य toolkit tabs का आफ्ना Apps Script references भए तिनीहरू हटाइएका छैनन्। त्यसैले ती tabs का features चलाउन पुरानो Apps Script deployment उपलब्ध हुनुपर्छ। SMC Chart भने GitHub-hosted JSON data बाट चल्छ र त्यसका लागि Google Apps Script आवश्यक छैन।

## Test checklist

Website खोल्दा पहिले full toolkit का tabs देखिनुपर्छ। त्यसपछि SMC Chart tab खोलेर:

1. Chart मा candles देखिन्छ कि जाँच गर्नुहोस्।
2. Date range वा instrument selector चलाउनुहोस्।
3. Browser DevTools वा Network मा `/data/chunks/manifest.json` र yearly JSON requests सफल छन् कि हेर्नुहोस्।
4. Actions run मा `Updated ...` वा valid no-op message आएको छ कि हेर्नुहोस्।

यदि website blank भयो भने पहिलो जाँच repository को नाम `FRIEND_USERNAME.github.io` नै छ कि छैन, र `index.html` तथा `data/` folder repository root मै छन् कि छैनन् भन्ने हो।

## Local test, optional

Python installed छ भने repository root मा:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -p "test_*.py"
python -m http.server 8000
```

त्यसपछि browser मा `http://localhost:8000/` खोल्नुहोस्। `index.html` लाई double-click गरेर `file://` बाट खोल्दा browser CORS restriction आउन सक्छ, त्यसैले local HTTP server प्रयोग गर्नुहोस्।

## Public sources

- [ShareSansar Market](https://www.sharesansar.com/market)
- [ShareSansar Today Share Price](https://www.sharesansar.com/today-share-price)
- [GitHub Actions workflow documentation](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions)
