unit:
	py.test -v

coverage:
	py.test --cov=downloader --cov-report=html --cov-report=term-missing
