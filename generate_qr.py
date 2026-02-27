import qrcode
import os


url = "http://127.0.0.1:5000"

print(f"Gerando QR Code para: {url}")


qr = qrcode.QRCode(
    version=1,  
    error_correction=qrcode.constants.ERROR_CORRECT_H,  
    box_size=10,  
    border=4,  
)

qr.add_data(url)
qr.make(fit=True)


img = qr.make_image(fill_color="#FFD60A", back_color="#0D1B2A")


os.makedirs("static/imgs", exist_ok=True)

output_path = "static/imgs/qrcode_cinevibe.png"
img.save(output_path)

print(f"✓ QR Code gerado com sucesso!")
print(f"✓ Ficheiro guardado em: {output_path}")
print(f"\nPodes ver o QR code:")
print(f"1. Abrindo o ficheiro: {output_path}")
print(f"2. No browser: http://127.0.0.1:5000/static/imgs/qrcode_cinevibe.png")
print(f"\nPara usar no site, adiciona ao HTML:")
print(f'<img src="{{{{ url_for(\'static\', filename=\'imgs/qrcode_cinevibe.png\') }}}}" alt="QR Code CineVibe">')
