"""邮件获取模块"""
import imaplib
import email
from email.header import decode_header
from typing import Optional, List, Tuple
from datetime import datetime

from .config import Config


def decode_chinese_text(text_bytes, encodings=['utf-8', 'gb2312', 'gbk', 'gb18030']) -> str:
    """尝试多种编码解码中文文本"""
    if isinstance(text_bytes, str):
        return text_bytes

    for encoding in encodings:
        try:
            return text_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue

    return text_bytes.decode('utf-8', errors='replace')


class EmailFetcher:
    """邮件获取器"""

    def __init__(self, username: str, password: str, imap_server: str = None):
        self.username = username
        self.password = password
        self.imap_server = imap_server or Config.EMAIL_IMAP_SERVER
        self.mail = None

    def login(self) -> bool:
        """登录邮箱"""
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server)
            self.mail.login(self.username, self.password)
            print(f"登录成功: {self.username}")
            return True
        except Exception as e:
            print(f"登录失败: {e}")
            return False

    def logout(self):
        """退出邮箱"""
        if self.mail:
            try:
                self.mail.logout()
                print("已退出邮箱")
            except Exception as e:
                print(f"退出失败: {e}")

    def fetch_emails_by_subject(
        self,
        target_subjects: List[str],
        folder: str = "INBOX",
        since_date: str = None
    ) -> List[Tuple[str, str]]:
        """
        根据邮件主题获取邮件

        Args:
            target_subjects: 目标主题列表（包含匹配）
            folder: 邮箱文件夹
            since_date: 起始日期，格式 "1-JAN-2025"

        Returns:
            [(html_content, date), ...] 邮件内容和日期列表
        """
        if not self.mail:
            print("请先登录邮箱")
            return []

        if since_date is None:
            # 默认获取当月的邮件
            now = datetime.now()
            since_date = datetime(now.year, now.month, 1).strftime("%d-%b-%Y")

        results = []
        try:
            self.mail.select(folder)
            status, messages = self.mail.search(None, f"SINCE {since_date}")

            if status != "OK":
                print("没有找到邮件")
                return []

            email_ids = list(reversed(messages[0].split()))
            print(f"找到 {len(email_ids)} 封邮件")

            # 先筛选匹配的邮件
            matching_ids = []
            for email_id in email_ids:
                res, msg = self.mail.fetch(email_id, "(BODY[HEADER.FIELDS (SUBJECT)])")
                if res != "OK":
                    continue

                header_str = decode_chinese_text(msg[0][1])
                subject_line = [l for l in header_str.split('\r\n') if l.startswith('Subject:')]

                if subject_line:
                    encoded_subject = subject_line[0].replace('Subject:', '').strip()
                    try:
                        decoded_parts = decode_header(encoded_subject)
                        subject = ""
                        for part, charset in decoded_parts:
                            if isinstance(part, bytes):
                                subject += part.decode(charset) if charset else decode_chinese_text(part)
                            else:
                                subject += part
                    except:
                        subject = encoded_subject

                    for target in target_subjects:
                        if target in subject:
                            matching_ids.append(email_id)
                            break

            print(f"匹配到 {len(matching_ids)} 封目标邮件")

            # 获取完整邮件内容
            for email_id in matching_ids:
                res, msg = self.mail.fetch(email_id, "(RFC822)")
                if res != "OK":
                    continue

                for response in msg:
                    if isinstance(response, tuple):
                        msg_obj = email.message_from_bytes(response[1])
                        date = msg_obj.get("Date")
                        html_content = self._extract_html_content(msg_obj)
                        if html_content:
                            results.append((html_content, date))

        except Exception as e:
            print(f"获取邮件失败: {e}")

        return results

    def _extract_html_content(self, msg_obj) -> Optional[str]:
        """从邮件对象中提取 HTML 内容"""
        if msg_obj.is_multipart():
            for part in msg_obj.walk():
                if part.get_content_type() == 'text/html':
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or 'utf-8'
                    return payload.decode(charset, errors='ignore')
        else:
            if msg_obj.get_content_type() == 'text/html':
                payload = msg_obj.get_payload(decode=True)
                charset = msg_obj.get_content_charset() or 'utf-8'
                return payload.decode(charset, errors='ignore')
        return None
