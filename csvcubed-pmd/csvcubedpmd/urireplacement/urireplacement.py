def replace(input, output, inputuri, outputuri):
    print("Hello, world.")
    while True:
        chunk = input.readline()
        if not chunk:
            break
        output.write(chunk)
        print(chunk)
    print(inputuri)
    print(outputuri)