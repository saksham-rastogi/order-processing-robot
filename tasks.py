from robocorp.tasks import task
from robocorp import browser,http
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
from RPA.FileSystem import FileSystem
import time


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
        slowmo=100,
    )
    open_robot_order_website()
    download_orders_data()
   
    orders_data=get_orders()
    for order in orders_data:
        close_annoying_modal()
        fill_the_form(order)
        receipt_pdf_path=store_receipt_as_pdf(order["Order number"])
        screenshot_path=screenshot_robot(order["Order number"])
        embed_screenshot_to_receipt(screenshot_path,receipt_pdf_path)
        go_to_another_robot()

    archive_receipts()

    


def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")


def download_orders_data():
    http.download("https://robotsparebinindustries.com/orders.csv","./output/orders.csv",overwrite=True)
    file_system=FileSystem()
    retry_count=0
    file_exists=False
    while retry_count< 3 and file_exists is False:
        file_exists=file_system.does_file_exist("./output/orders.csv")
        retry_count=retry_count+1
        time.sleep(2)

    

def get_orders():
    tables=Tables()
    orders_data=tables.read_table_from_csv(path="./output/orders.csv",header=True)
    return orders_data

def close_annoying_modal():
    page = browser.page()
    page.click('//div[@class="alert-buttons"]//button[text()="OK"]')



def fill_the_form(order):
    page= browser.page()
    page.select_option("#head",order["Head"])
    page.click('//input[@value='+order["Body"]+']')
    page.fill('//label[text()="3. Legs:"]/ancestor::div/input',order["Legs"])
    page.fill("#address",order["Address"])
    page.click("#preview")

    page.click("#order")
    retry_count=0
    while page.is_visible(selector='//div[@class="alert alert-danger"]',timeout=60) and retry_count <3:
        page.click("#order")
        retry_count=retry_count + 1
        time.sleep(2)
        
    

    

    
def store_receipt_as_pdf(order_number):
    page=browser.page()
    receipt_html=page.locator("#receipt").inner_html()
    pdf=PDF()
    pdf.html_to_pdf(receipt_html,"./output/receipts/"+order_number+" receipt.pdf")
    return "./output/receipts/"+order_number+" receipt.pdf"
    

def screenshot_robot(order_number):
    page = browser.page()
    page.locator("#robot-preview-image").screenshot(path="./output/roboimage/robo_"+order_number+".png")
    return "./output/roboimage/robo_"+order_number+".png"

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf=PDF()
    # list_of_files=[pdf_file,screenshot]
    pdf.add_files_to_pdf(files=[pdf_file,screenshot],target_document=pdf_file)

def go_to_another_robot():
    browser.page().click("#order-another")

def archive_receipts():
    archive = Archive()
    archive.archive_folder_with_zip(folder="./output/receipts",archive_name="./output/receipts.zip")
    





