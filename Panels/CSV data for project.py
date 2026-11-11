import yfinance as yf
vix = yf.Ticker("^VIX")
sp = yf.Ticker("^GSPC")
fsetf = yf.Ticker("XLF")
nasd = yf.Ticker("^NDX")
russ = yf.Ticker("^RUT")

dfvix = yf.download("^VIX", start = "2007-01-01", end = "2026-01-01")
outputfile1 = "vix.csv"
dfvix.to_csv(outputfile1)

dfsp = yf.download("^GSPC", start = "2007-01-01", end = "2026-01-01")
outputfile2 = "sp.csv"
dfsp.to_csv(outputfile2)

dffsetf = yf.download("XLF", start = "2007-01-01", end = "2026-01-01")
outputfile3 = "fsetf.csv"
dffsetf.to_csv(outputfile3)

dfnasd = yf.download("^NDX", start = "2007-01-01", end = "2026-01-01")
outputfile4 = "nasd.csv"
dfnasd.to_csv(outputfile4)

dfruss = yf.download("^RUT", start = "2007-01-01", end = "2026-01-01")
outputfile5 = "russ.csv"
dfruss.to_csv(outputfile5)