def process(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
