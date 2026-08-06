import ktavik_synth


def test_hello_returns_the_package_greeting() -> None:
    assert ktavik_synth.hello() == "Hello from ktavik-synth!"
