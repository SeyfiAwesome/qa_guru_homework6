from datetime import date


def normalize_addresses(value: str) -> str:
    normalized_value = value.strip().lower()
    return normalized_value


"""Возвращает значение, в котором адрес приведен к нижнему регистру и очищен от пробелов по краям"""


def add_short_body(email: dict) -> dict:
    email['short_body'] = email['body'][:10] = "..."
    return email


"""Возвращает email с новым ключом email["short_body"] — первые 10 символов тела письма + "..."."""


def clean_body_text(body: str) -> str:
    text = body.replace('\n', ' ').replace('\t', ' ')
    while "  " in text:
        text = text.replace("  ", " ")
    return text


"""Заменяет табы и переводы строк на пробелы. """


def build_sent_text(email: dict) -> str:
    recipient = email.get('recipient', '')
    sender = email.get('sender', '')
    subject = email.get('subject', '')
    send_date = email.get('date', '')
    body = email.get('short_body')

    return f"""Кому: {recipient}, от {sender}
    Тема: {subject}, дата {send_date}
    {body}"""


"""Формирует текст письма в формате:
Кому: {to}, от {from}
Тема: {subject}, дата
{date} {clean_body}"""


def check_empty_fields(subject: str, body: str) -> tuple[bool, bool]:
    """
    Проверяет, пусты ли поля subject и body.
    Возвращает кортеж (is_subject_empty, is_body_empty):
        True, если соответствующее поле пустое, иначе False.
    """
    is_subject_empty = subject.strip() == ""
    is_body_empty = body.strip() == ""
    return is_subject_empty, is_body_empty


'''Возвращает кортеж (is_subject_empty, is_body_empty). True, если поле пустое.'''


def mask_sender_email(login: str, domain: str):
    mask_form = login[:2] + "***@" + domain
    return mask_form


"""Возвращает маску email: первые 2 символа логина + "***@" + домен."""


def get_correct_email(email_list: list[str]) -> list[str]:
    correct_email_list = []

    for email in email_list:
        email = email.strip()
        if not email:
            continue
        if "@" not in email:
            continue
        email_lower = email.lower()
        if email_lower.endswith(('.com', '.ru', '.net')):
            correct_email_list.append(email)
    return correct_email_list


"""Возвращает список корректных email."""


def create_email(sender: str, recipient: str, subject: str, body: str) -> dict:
    email_dict = {
        'sender': sender,
        'recipient': recipient,
        'subject': subject,
        'body': body
    }
    return email_dict


"""Создает словарь email с базовыми полями: 'sender', 'recipient', 'subject', 'body'"""


def add_send_date(email: dict) -> dict:
    current_day = date.today()
    formatted_current_day = str(current_day)
    email['date'] = formatted_current_day
    return email


"""Возвращает email с добавленным ключом email["date"] — текущая дата в формате YYYY-MM-DD."""


def extract_login_domain(address: str) -> tuple[str, str]:
    adress_parts = address.split('@')

    if len(adress_parts) == 2:
        login = adress_parts[0]
        domain = adress_parts[1]
        return login, domain
    else:
        raise ValueError(f"Not a valid email address: {address}")


'''Возвращает логин и домен отправителя. Пример: "user@mail.ru" -> ("user", "mail.ru")'''


def sender_email(recipient_list: list[str], subject: str, message: str, *, sender="default@study.com") -> list[dict]:
    """
    Главная функция для обработки и "отправки" писем.
    """

    if not recipient_list:
        return []

    all_emails = recipient_list + [sender]
    correct_emails = get_correct_email(all_emails)

    if sender not in correct_emails:
        return []

    valid_recipients = [email for email in recipient_list if email in correct_emails]

    is_subject_empty, is_body_empty = check_empty_fields(subject, message)
    if is_subject_empty or is_body_empty:
        return []

    final_recipients = []
    for recipient in valid_recipients:
        if normalize_addresses(recipient) != normalize_addresses(sender):
            final_recipients.append(recipient)

    if not final_recipients:
        return []

    normalized_subject = clean_body_text(subject)
    normalized_body = clean_body_text(message)
    normalized_sender = normalize_addresses(sender)

    result_emails = []

    for recipient in final_recipients:
        normalized_recipient = normalize_addresses(recipient)

        email_dict = create_email(
            sender=normalized_sender,
            recipient=normalized_recipient,
            subject=normalized_subject,
            body=normalized_body
        )

        email_dict = add_send_date(email_dict)

        login, domain = extract_login_domain(email_dict['sender'])
        email_dict['masked_sender'] = mask_sender_email(login, domain)

        email_dict = add_short_body(email_dict)

        sent_text = build_sent_text(email_dict)
        email_dict['sent_text'] = sent_text

        result_emails.append(email_dict)

    return result_emails
