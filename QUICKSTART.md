# 🚀 Quick Start Guide

Get the European Youth Portal Scraper - Professional Edition up and running in minutes!

## ⚡ 5-Minute Setup

### 1. Prerequisites
- Python 3.8 or higher
- pip package manager
- Internet connection

### 2. Installation
```bash
# Clone or download the project
cd europayouthscraper

# Install dependencies
pip install -r requirements.txt
```

### 3. First Run
```bash
# Run the quick demo
python main_professional.py

# If you see the demo output, you're ready to go! 🎉
```

## 🎯 Essential Commands

### Collect Data
```bash
# Scrape fresh opportunities (takes 5-15 minutes)
python main_professional.py scrape
```

### Explore Data
```bash
# View statistics
python main_professional.py stats

# Search for opportunities in Turkey
python main_professional.py query --country "Turkey"

# Search by topic
python main_professional.py query --topic "Environment"

# Interactive exploration
python main_professional.py interactive
```

### Export Data
```bash
# Export to Excel
python main_professional.py export --format excel

# Export filtered data
python main_professional.py export --format csv --country "Germany"
```

## 🔧 Common Use Cases

### 1. Country-Specific Research
```bash
# Find all opportunities for Turkish participants
python main_professional.py query --country "Turkey" --format detailed

# Export Turkey opportunities to Excel
python main_professional.py export --format excel --country "Turkey" --filename "turkey_opportunities.xlsx"
```

### 2. Topic-Based Analysis
```bash
# Environment-related opportunities
python main_professional.py query --topic "Environment" --limit 20

# Multiple topics
python main_professional.py query --topic "Environment" --topic "Climate" --topic "Sustainability"
```

### 3. Location-Based Search
```bash
# Opportunities in Berlin
python main_professional.py query --location "Berlin"

# Opportunities in Italy
python main_professional.py query --location "Italy" --format detailed
```

### 4. Complex Filtering
```bash
# Environment opportunities in Germany for Turkish participants
python main_professional.py query \
  --country "Turkey" \
  --topic "Environment" \
  --location "Germany" \
  --format detailed
```

### 5. Analytics & Insights
```bash
# Run analytics demo
python main_professional.py analytics-demo

# View comprehensive statistics
python main_professional.py stats --format json > analytics.json
```

## 📊 Sample Output

### Stats Command
```
📊 Database contains 1,245 opportunities

🌍 Top 5 Countries:
   1. Germany: 156 opportunities
   2. France: 142 opportunities  
   3. Italy: 134 opportunities
   4. Spain: 128 opportunities
   5. Poland: 95 opportunities

🎯 Top 5 Topics:
   1. Environment: 234 opportunities
   2. Culture: 198 opportunities
   3. Education: 187 opportunities
   4. Youth: 156 opportunities
   5. Social: 145 opportunities
```

### Query Command
```
🔍 Executing Advanced Query
Found 23 opportunities (showing 10)
Query time: 0.045 seconds

┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ ID         ┃ Title                                   ┃ Location           ┃ Countries          ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ 12345      │ Environmental Protection Project        │ Berlin, Germany    │ Turkey, Germany... │
│ 12346      │ Climate Action Youth Initiative         │ Munich, Germany    │ Turkey, Poland...  │
└────────────┴─────────────────────────────────────────┴────────────────────┴────────────────────┘
```

## 🛠️ Troubleshooting

### Installation Issues
```bash
# If you get permission errors
pip install --user -r requirements.txt

# If you have multiple Python versions
python3 -m pip install -r requirements.txt
```

### No Data Found
```bash
# First scrape some data
python main_professional.py scrape

# Then run queries
python main_professional.py query --country "Turkey"
```

### Slow Performance
```bash
# Use fewer workers for slower connections
python main_professional.py scrape --workers 5 --rate-limit 7.0
```

## 📚 Next Steps

1. **Read the Full Documentation**: Check `README.md` for complete features
2. **Explore Analytics**: Run `python main_professional.py analytics-demo`
3. **Try Interactive Mode**: `python main_professional.py interactive`
4. **Export Your Data**: Use various export formats for external analysis
5. **Customize Configuration**: Edit `config.py` for your needs

## 🆘 Need Help?

- Run any command with `--help` for detailed options
- Check the `logs/scraper.log` file for detailed logging
- View the comprehensive `README.md` for advanced features
- Create an issue if you encounter problems

---

**Happy Scraping! 🎉** 