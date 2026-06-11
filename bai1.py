import functools
import logging
import os
import sys
import unittest

# =====================================================================
# CẤU HÌNH LOGGING SYSTEM
# =====================================================================
logging.basicConfig(
    filename="momo_transactions.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

# =====================================================================
# ĐỊNH NGHĨA NGOẠI LỆ (CUSTOM EXCEPTIONS)
# =====================================================================
class InvalidAmountError(Exception):
    """Ngoại lệ xảy ra khi số tiền giao dịch nhỏ hơn hoặc bằng 0."""
    pass


class InsufficientBalanceError(Exception):
    """Ngoại lệ xảy ra khi số dư tài khoản không đủ để thực hiện giao dịch."""
    pass


# Biến toàn cục quản lý số dư của ví MoMo
current_balance = 0.0


# =====================================================================
# CÁC HÀM NGHIỆP VỤ CỐT LÕI (FUNCTIONS)
# =====================================================================
def check_empty(text_input):
    """Kiểm tra dữ liệu nhập vào có bị bỏ trống hay không."""
    return not text_input.strip()


def get_valid_amount(prompt):
    """Hàm ép kiểu và bắt lỗi định dạng ValueError khi người dùng nhập chữ."""
    while True:
        try:
            amount_input = input(prompt).strip()
            return float(amount_input)
        except ValueError:
            print("\nLỗi: Vui lòng nhập số tiền hợp lệ.")
            logging.error("ValueError: Invalid numeric input for deposit.")


def deposit_money(amount):
    """
    Xử lý nghiệp vụ nạp tiền vào ví.
    
    Args:
        amount (float): Số tiền cần nạp vào hệ thống.
    """
    global current_balance

    if amount <= 0:
        logging.error(f"InvalidAmountError: Attempted to process {int(amount)} VND.")
        raise InvalidAmountError("Số tiền giao dịch phải lớn hơn 0.")

    current_balance += amount

    print(f"\nNạp tiền thành công: +{amount:,.0f} VND")
    print(f"Số dư hiện tại: {current_balance:,.0f} VND")
    logging.info(f"Deposit successful: +{int(amount)} VND. Current Balance: {int(current_balance)}")


def transfer_money(phone, amount):
    """
    Xử lý nghiệp vụ chuyển tiền đến số điện thoại nhận.
    
    Args:
        phone (str): Số điện thoại gồm 10 chữ số.
        amount (float): Số tiền cần chuyển đi.
    """
    global current_balance

    if amount <= 0:
        logging.error(f"InvalidAmountError: Attempted to process {int(amount)} VND.")
        raise InvalidAmountError("Số tiền giao dịch phải lớn hơn 0.")

    if amount > current_balance:
        logging.error(f"InsufficientBalanceError: Attempted to transfer {int(amount)} VND with balance {int(current_balance)} VND.")
        raise InsufficientBalanceError("Giao dịch thất bại: Số dư của bạn không đủ.")

    if amount >= 10000000:
        logging.warning(f"High value transaction detected: {int(amount)} VND to {phone}")

    current_balance -= amount

    print(f"\nChuyển tiền thành công tới số điện thoại {phone}.")
    print(f"Số tiền đã chuyển: {amount:,.0f} VND")
    print(f"Số dư còn lại: {current_balance:,.0f} VND")
    logging.info(f"Transfer successful: -{int(amount)} VND to {phone}. Current Balance: {int(current_balance)}")


def read_system_logs():
    """Chức năng 3: Đọc file log và lọc ra 5 sự kiện gần đây nhất."""
    log_file = "momo_transactions.log"
    print("\n--- 5 SỰ KIỆN GẦN NHẤT TRONG HỆ THỐNG ---")

    if not os.path.exists(log_file) or os.path.getsize(log_file) == 0:
        print("Chưa có lịch sử giao dịch nào trong hệ thống.")
        return

    try:
        with open(log_file, "r", encoding="utf-8") as file:
            lines = file.readlines()
            recent_events = lines[-5:]
            for idx, log_item in enumerate(recent_events, 1):
                print(f"{idx}. {log_item.strip()}")
    except IOError as e:
        print(f"Lỗi đọc file từ hệ thống: {e}")


# =====================================================================
# KỊCH BẢN KIỂM THỬ TỰ ĐỘNG (UNIT TEST CASES)
# =====================================================================
class TestWalletEngine(unittest.TestCase):
    """Lớp kiểm thử các hàm tính toán và bẫy lỗi của ví MoMo."""

    def setUp(self):
        """Reset số dư ví về 0 trước khi chạy mỗi bài test case."""
        global current_balance
        current_balance = 0.0

    def test_deposit_success(self):
        """Kiểm tra nạp tiền chính xác có làm tăng số dư không."""
        deposit_money(500000.0)
        self.assertEqual(current_balance, 500000.0, "Lỗi: Số dư tính sai khi nạp thành công.")

    def test_transfer_insufficient_balance(self):
        """Kiểm tra hàm chuyển tiền xem có chủ động ném lỗi nếu thiếu tiền không."""
        global current_balance
        current_balance = 300000.0
        with self.assertRaises(InsufficientBalanceError):
            transfer_money("0987654321", 500000.0)

    def test_invalid_amount(self):
        """Kiểm tra xem hệ thống có chặn và ném lỗi khi nạp số tiền âm không."""
        with self.assertRaises(InvalidAmountError):
            deposit_money(-100000.0)


# =====================================================================
# HÀM ĐIỀU KHIỂN TRUNG TÂM (MAIN)
# =====================================================================
def main():
    global current_balance

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

        if check_empty(choice):
            print("\nLựa chọn không được bỏ trống!")
            continue

        match choice:
            case "1":
                print("\n--- NẠP TIỀN VÀO VÍ ---")
                amount = get_valid_amount("Nhập số tiền cần nạp: ")
                try:
                    deposit_money(amount)
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
                    transfer_money(phone, amount)
                except (InvalidAmountError, InsufficientBalanceError) as e:
                    print(f"\n{e}")
                    if isinstance(e, InsufficientBalanceError):
                        print(f"Số dư hiện tại: {current_balance:,.0f} VND")

            case "3":
                read_system_logs()

            case "4":
                print("\n--- SỐ DƯ VÍ MOMO ---")
                print(f"Số dư hiện tại: {current_balance:,.0f} VND")
                logging.info(f"Balance checked. Current Balance: {int(current_balance)}")

            case "5":
                print("\nCảm ơn bạn đã sử dụng dịch vụ")
                logging.info("System shutdown")
                
                print("\n[HỆ THỐNG] Đang tự động chạy Unit Test kiểm tra logic...")
                print("=" * 60)
                
                # Kích hoạt chạy bộ kiểm thử tự động trước khi đóng file
                suite = unittest.TestLoader().loadTestsFromTestCase(TestWalletEngine)
                runner = unittest.TextTestRunner(verbosity=2)
                runner.run(suite)
                
                print("=" * 60)
                sys.exit(0)

            case _:
                print("\nLựa chọn không hợp lệ, vui lòng chọn từ 1 đến 5.")


if __name__ == "__main__":
    main()