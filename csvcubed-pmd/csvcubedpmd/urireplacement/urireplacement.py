def replace(input, output):
    print("Hello, world.")
    while True:
        chunk = input.readline()
        if not chunk:
            break
        output.write(chunk)
        print(chunk)