
clean:
	rm -rf __pycache__
	rm -rf plasma/__pycache__

listen:
	@python3 -m plasma.event_listener

run:
	@python3 -m plasma