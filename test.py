

num = [2, 4 , 5 ,6]
def teaser(numbers):
    for index in range(1, len(numbers)):
        if numbers[index] > numbers[index - 1]:
            return False
    return True


teaser(num)