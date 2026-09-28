from utils import load_faqs, save_faq


# 將 FAQ 按照 ID 排序，並儲存。
def sort_faqs_by_id():
    faqs = load_faqs()
    faqs.sort(key=lambda faq: faq["id"])
    save_faq(faqs)
    return faqs