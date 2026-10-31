import io
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image, ImageDraw, ImageFont

class CounterQrService:
    def generate_counter_qr_bytes(self, checkout_url: str, business_name: str = "Sharma Kirana Store") -> bytes:
        """Generates a high-resolution Paytm-styled Counter QR Code image as PNG bytes."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(checkout_url)
        qr.make(fit=True)

        # Paytm Navy Blue: #002e6e -> (0, 46, 110)
        img = qr.make_image(
            fill_color="#002e6e",
            back_color="white"
        )

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

qr_service = CounterQrService()
