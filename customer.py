from faq_service import search_faq
def service_ai(user_question):
    
    service_return=search_faq(user_question)
    print(service_return)
    return (service_return)