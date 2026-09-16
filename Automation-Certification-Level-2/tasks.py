from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Tables import Tables
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=50,
    )
    open_robot_order_website()
    orders = get_orders()
    close_annoying_modal()
    for row in orders:
        fill_the_form(row)
        preview_robot(row)
        submit_order()
        store_receipt_as_pdf(row["Order number"])
        embed_screenshot_to_receipt(f"output/screenshots/robot_{row['Order number']}.png", f"output/receipts/receipt_{row['Order number']}.pdf")
        close_annoying_modal()
        archive_receipts()

def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    """Downloads orders file (CSV) from the given URL, read it as a table and return the result"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    orders = Tables().read_table_from_csv("orders.csv", header=True)
    return orders

def fill_the_form(row):
    """Fills the form"""
    page = browser.page()

    page.select_option("#head", str(row["Head"]))
    page.locator(f'input[type="radio"][name="body"][value="{row["Body"]}"]').check()
    page.fill('input[placeholder="Enter the part number for the legs"]',str(row["Legs"]))
    page.fill("#address", row["Address"])

def close_annoying_modal():
    """Closes the annoying modal that appers when you open the website"""
    page = browser.page()
    page.click("text=OK")

def preview_robot(row):
    """Previews the robot and saves the screenshot of the page"""
    page = browser.page()
    page.click("text=Preview")
    page.locator("#robot-preview-image").screenshot(path=f"output/screenshots/robot_{row['Order number']}.png")

def submit_order():
    """Submits the order"""
    page = browser.page()
    page.click("#order")
    while not page.locator("text=Order another robot").is_visible():
        page.wait_for_timeout(200)
        page.click("#order")


def store_receipt_as_pdf(order_number):
    """Saves the order receipt as a PDF file"""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf.html_to_pdf(receipt_html, f"output/receipts/receipt_{order_number}.pdf")
    page.click("text=Order another robot")

def embed_screenshot_to_receipt(screenshot, pdf_file):

    """Embeds the screenshot of the robot to the PDF receipt"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(screenshot, pdf_file, pdf_file)

def archive_receipts():
    """Creates ZIP archive of the receipts with the embedded images"""
    archive = Archive()
    archive.archive_folder_with_zip("output/receipts", "output/receipts.zip")
