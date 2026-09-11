from faq_service import search_faq
def service_ai(user_question):
    service_return=search_faq(user_question)
    if service_return is None:
        print ("為找到問題，請重新輸入")
        return None
    else:
        print (f"客服小劉:{service_return}")
        return (service_return)