# from database.db import get_db
# import hashlib
# import secrets
# from typing import Optional, Dict, Any
#
#
# def verify_user(username: str, password: str) -> Optional[Dict[str, Any]]:
#     """
#     Xác thực người dùng và trả về thông tin user nếu hợp lệ
#
#     Args:
#         username: Tên đăng nhập
#         password: Mật khẩu (chưa băm)
#
#     Returns:
#         Thông tin người dùng nếu xác thực thành công, None nếu thất bại
#     """
#     with get_db() as conn:
#         user = conn.execute(
#             """
#             SELECT * FROM user
#             WHERE username = ? AND is_deleted = 0
#             """,
#             (username,)
#         ).fetchone()
#
#         if not user:
#             return None
#
#         # Băm mật khẩu nhập vào và so sánh với hash lưu trong db
#         hashed_password = hashlib.sha256(password.encode()).hexdigest()
#         if hashed_password == user['password_hash']:
#             return dict(user)
#
#         return None
#
#
# def create_session(user_id: int) -> str:
#     """
#     Tạo session mới và lưu vào database
#
#     Args:
#         user_id: ID của người dùng
#
#     Returns:
#         Token session mới được tạo
#     """
#     session_token = secrets.token_hex(32)
#     with get_db() as conn:
#         conn.execute(
#             """
#             INSERT INTO user_session (user_id, session_token, expires_at)
#             VALUES (?, ?, datetime('now', '+1 day'))
#             """,
#             (user_id, session_token)
#         )
#         conn.commit()
#     return session_token
#
#
# def verify_session(session_token: str) -> Optional[Dict[str, Any]]:
#     """
#     Xác thực session và trả về thông tin user nếu hợp lệ
#
#     Args:
#         session_token: Token session cần xác thực
#
#     Returns:
#         Thông tin người dùng nếu session hợp lệ, None nếu không hợp lệ
#     """
#     if not session_token:
#         return None
#
#     with get_db() as conn:
#         session = conn.execute(
#             """
#             SELECT u.*
#             FROM user_session us
#             JOIN user u ON us.user_id = u.user_id
#             WHERE us.session_token = ?
#               AND us.expires_at > datetime('now')
#               AND us.is_revoked = 0
#               AND u.is_deleted = 0
#             """,
#             (session_token,)
#         ).fetchone()
#
#         if session:
#             return dict(session)
#         return None
#
#
# def revoke_session(session_token: str) -> None:
#     """
#     Hủy bỏ một session
#
#     Args:
#         session_token: Token session cần hủy bỏ
#     """
#     with get_db() as conn:
#         conn.execute(
#             """
#             UPDATE user_session
#             SET is_revoked = 1
#             WHERE session_token = ?
#             """,
#             (session_token,)
#         )
#         conn.commit()
#
#
# def change_password(user_id: int, current_password: str, new_password: str) -> bool:
#     """
#     Đổi mật khẩu cho người dùng
#
#     Args:
#         user_id: ID của người dùng
#         current_password: Mật khẩu hiện tại (chưa băm)
#         new_password: Mật khẩu mới (chưa băm)
#
#     Returns:
#         True nếu đổi mật khẩu thành công, False nếu thất bại
#     """
#     with get_db() as conn:
#         # Lấy thông tin user
#         user = conn.execute(
#             """
#             SELECT * FROM user
#             WHERE user_id = ? AND is_deleted = 0
#             """,
#             (user_id,)
#         ).fetchone()
#
#         if not user:
#             return False
#
#         # Xác thực mật khẩu hiện tại
#         current_hash = hashlib.sha256(current_password.encode()).hexdigest()
#         if current_hash != user['password_hash']:
#             return False
#
#         # Cập nhật mật khẩu mới
#         new_hash = hashlib.sha256(new_password.encode()).hexdigest()
#         conn.execute(
#             """
#             UPDATE user
#             SET password_hash = ?
#             WHERE user_id = ?
#             """,
#             (new_hash, user_id)
#         )
#
#         # Hủy tất cả các session cũ
#         conn.execute(
#             """
#             UPDATE user_session
#             SET is_revoked = 1
#             WHERE user_id = ?
#             """,
#             (user_id,)
#         )
#
#         conn.commit()
#         return True
#
#
# def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
#     """
#     Lấy thông tin người dùng theo ID
#
#     Args:
#         user_id: ID của người dùng cần lấy thông tin
#
#     Returns:
#         Thông tin người dùng nếu tìm thấy, None nếu không tìm thấy
#     """
#     with get_db() as conn:
#         user = conn.execute(
#             """
#             SELECT * FROM user
#             WHERE user_id = ? AND is_deleted = 0
#             """,
#             (user_id,)
#         ).fetchone()
#
#         return dict(user) if user else None