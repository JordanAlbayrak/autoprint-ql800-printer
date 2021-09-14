from PIL import Image
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster
import discord
import os
import requests

TOKEN = os.environ.get('TOKEN')

backend = 'pyusb'  # 'pyusb', 'linux_kernel', 'network'
model = 'QL-800'  # your printer model.
printer = 'usb://0x04F9:0x209B'  # Get these values from the Windows usb driver filter.  Linux/Raspberry Pi uses '/dev/usb/lp0'.

qlr = BrotherQLRaster(model)
qlr.exception_on_warning = True


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        if len(message.attachments) > 0 and message.attachments[0].url:
            img_url = message.attachments[0].url
            img_bin = requests.get(img_url)
            img_name = img_url.split("/")[-1]
            with open(img_name, 'wb') as f:
                f.write(img_bin.content)

            im = Image.open(img_name)
            im.resize((306, 991))
            print_image(im)
            os.remove(img_name)


client = MyClient()


def print_image(im):

    instructions = convert(

        qlr=qlr,
        images=[im],  # Takes a list of file names or PIL objects.
        label='62red',
        rotate='90',  # 'Auto', '0', '90', '270'
        threshold=70.0,  # Black and white threshold in percent.
        dither=False,
        compress=False,
        red=True,  # Only True if using Red/Black 62 mm label tape.
        dpi_600=False,
        hq=True,  # False for low quality.
        cut=True

    )

    send(instructions=instructions, printer_identifier=printer, backend_identifier=backend, blocking=True)


client.run(TOKEN)
