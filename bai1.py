import logging
import os
import sys

# Cấu hình logging theo định dạng yêu cầu của hệ thống
logging.basicConfig(
    filename="momo_transactions.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)


class InvalidAmountError(Exception):
    """Ngoại lệ xảy ra khi số tiền giao dịch nhỏ hơn hoặc bằng 0."""
    pass


class InsufficientBalanceError(Exception):
    """Ngoại lệ xảy ra khi số dư tài khoản không đủ để chuyển tiền."""
    pass


class Wallet:
    """
    Lớp quản lý tài khoản ví điện tử cá nhân.
    
    Thuộc tính:
        _balance (float): Số dư hiện tại của tài khoản ví.
    """

    def __init__(self):
        """Khởi tạo ví điện tử với số dư mặc định bằng 0."""
        self._balance = 0.0

    @property
    def balance(self):
        """Lấy số dư hiện tại của ví."""
        return self._balance

    def deposit(self, amount):
        """
        Nạp tiền vào tài khoản ví điện tử.

        Args:
            amount (float): Số tiền người dùng muốn nạp.

        Raises:
            InvalidAmountError: Nếu số tiền nạp nhỏ hơn hoặc bằng 0.
        """
        if amount <= 0:
            logging.error(f"InvalidAmountError: Attempted to process "
                          f"{int(amount)} VND.")
            raise InvalidAmountError("Số tiền giao dịch phải lớn hơn 0.")

        self._balance += amount
        logging.info(f"Deposit successful: +{int(amount)} VND. "
                     f"Current Balance: {int(self._balance)}")

    def transfer(self, phone, amount):
        """
        Chuyển tiền từ tài khoản ví đến một số điện thoại nhận.

        Args:
            phone (str): Số điện thoại người nhận (10 chữ số).
            amount (float): Số tiền cần chuyển đi.

        Raises:
            InvalidAmountError: Nếu số tiền chuyển nhỏ hơn hoặc bằng 0.
            InsufficientBalanceError: Nếu số tiền chuyển vượt quá số dư ví.
        """
        if amount <= 0:
            logging.error(f"InvalidAmountError: Attempted to process "
                          f"{int(amount)} VND.")
            raise InvalidAmountError("Số tiền giao dịch phải lớn hơn 0.")

        if amount > self._balance:
            logging.error(f"InsufficientBalanceError: Attempted to transfer "
                          f"{int(amount)} VND with balance "
                          f"{int(self._balance)} VND.")
            raise InsufficientBalanceError("Số dư của bạn không đủ.")

        if amount >= 10000000:
            logging.warning(f"High value transaction detected: "
                            f"{int(amount)} VND to {phone}")

        self._balance -= amount
        logging.info(f"Transfer successful: -{int(amount)} VND to {phone}. "
                     f"Current Balance: {int(self._balance)}")


def get_valid_amount(prompt):
    """
    Ép kiểu và bắt lỗi đầu vào số tiền từ bàn phím.

    Args:
        prompt (str): Câu lệnh hướng dẫn nhập dữ liệu.

    Returns:
        float: Số tiền hợp lệ kiểu số thực.
    """
    while True:
        try:
            user_input = input(prompt).strip()
            return float(user_input)
        except ValueError:
            print("\nLỗi: Vui lòng nhập số tiền hợp lệ.")
            logging.error("ValueError: Invalid numeric input for deposit.")


def read_system_logs():
    """Đọc file log và hiển thị 5 sự kiện giao dịch gần nhất."""
    log_file = "momo_transactions.log"
    print("\n--- 5 SỰ KIỆN GẦN NHẤT TRONG HỆ THỐNG ---")

    if not os.path.exists(log_file) or os.path.getsize(log_file) == 0:
        print("Chưa có lịch sử giao dịch nào trong hệ thống.")
        return

    try:
        with open(log_file, "r", encoding="utf-8") as file:
            lines = file.readlines()
            # Lấy tối đa 5 dòng nhật ký cuối cùng
            recent_logs = lines[-5:]
            for idx, log in enumerate(recent_logs, 1):
                print(f"{idx}. {log.strip()}")
    except IOError as e:
        print(f"Lỗi hệ thống khi đọc lịch sử: {e}")


def main():
    """Luồng điều khiển chính và giao diện dòng lệnh của ứng dụng."""
    wallet = Wallet()

    while True:
        menu = """
========== VÍ MOMO GIẢ LẬP ==========
1. Nạp tiền vào ví
2. Chuyển tiền
3. Xem lịch sử hệ thống
4. Xem số dư tài khoản
5. Thoát chương trình 
=============================================== """
        print(menu)
        choice = input("Chọn chức năng (1-5): ").strip()

        match choice:
            case "1":
                print("\n--- NẠP TIỀN VÀO VÍ ---")
                amount = get_valid_amount("Nhập số tiền cần nạp: ")
                try:
                    wallet.deposit(amount)
                    print(f"\nNạp tiền thành công: +{amount:,.0f} VND")
                    print(f"Số dư hiện tại: {wallet.balance:,.0f} VND")
                except InvalidAmountError as e:
                    print(f"Lỗi: {e}")

            case "2":
                print("\n--- CHUYỂN TIỀN ---")
                phone = input("Nhập số điện thoại người nhận: ").strip()
                if len(phone) != 10 or not phone.isdigit():
                    print("\nLỗi: Số điện thoại người nhận phải đúng 10 số.")
                    continue

                amount = get_valid_amount("Nhập số tiền cần chuyển: ")
                try:
                    wallet.transfer(phone, amount)
                    print(f"\nChuyển tiền thành công tới số điện thoại {phone}.")
                    print(f"Số tiền đã chuyển: {amount:,.0f} VND")
                    print(f"Số dư còn lại: {wallet.balance:,.0f} VND")
                except (InvalidAmountError, InsufficientBalanceError) as e:
                    print(f"\nGiao dịch thất bại: {e}")
                    if isinstance(e, InsufficientBalanceError):
                        print(f"Số dư hiện tại: {wallet.balance:,.0f} VND")

            case "3":
                read_system_logs()

            case "4":
                print("\n--- SỐ DƯ VÍ MOMO ---")
                print(f"Số dư hiện tại: {wallet.balance:,.0f} VND")
                logging.info(f"Balance checked. Current Balance: "
                             f"{int(wallet.balance)}")

            case "5":
                print("\nCảm ơn bạn đã sử dụng dịch vụ")
                logging.info("System shutdown")
                sys.exit(0)

            case _:
                print("\nLựa chọn không hợp lệ, vui lòng chọn từ 1 đến 5.")


if __name__ == "__main__":
    main()