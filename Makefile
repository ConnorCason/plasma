
clean:
	rm -rf __pycache__
	rm -rf plasma/__pycache__

fee-balance:
	@python3 -m plasma.fee-balance

listen:
	@python3 -m plasma.event_listener

install:
	@python3 -m pip install -r requirements.txt

run:
	@python3 -m plasma