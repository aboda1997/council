def create_arabic_format(user_input):
    srchSt = ""
    for i in range(len(user_input)):
        if (
            user_input[i] == "آ"
            or user_input[i] == "ا"
            or user_input[i] == "أ"
            or user_input[i] == "إ"
        ):
            srchSt += ("+(إ|أ|ا|آ)", "(إ|أ|ا|آ)")[srchSt == ""]
        elif user_input[i] == "ة" or user_input[i] == "ه":
            srchSt += ("+(ة|ه)", "(ة|ه)")[srchSt == ""]
        elif user_input[i] == "ى" or user_input[i] == "ي":
            srchSt += ("+(ي|ى)", "(ي|ى)")[srchSt == ""]
        else:
            srchSt += user_input[i]
    return srchSt


def create_multiple_spaces_format(user_input):
    return r"\s+".join(user_input.split())
