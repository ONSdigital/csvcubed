def replace(input, output):
    print("Hello, world.")
    while True:
        chunk = input.read(512)
        if not chunk:
            break
        output.write(chunk)
        print(chunk)