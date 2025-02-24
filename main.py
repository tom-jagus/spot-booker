import os
from datetime import datetime as dt
from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio

TIMEOUT = 10
SPOT_URL = os.environ["SPOT_URL"]
SPOT_UN = os.environ["SPOT_UN"]
SPOT_PS = os.environ["SPOT_PS"]
TODAY = dt.today()
TARGET_DATE = f"{TODAY.day + 1}-{TODAY.month:02}"


async def main():
    options = webdriver.ChromeOptions()
    options.headless = False

    async with webdriver.Chrome(options=options) as browser:
        await browser.get(SPOT_URL, wait_load=True)
        await browser.sleep(3)
        inp_signInName = await browser.find_element(
            By.ID, "signInName", timeout=TIMEOUT
        )
        await inp_signInName.send_keys(SPOT_UN)
        btn_continue = await browser.find_element(By.ID, "continue")
        await btn_continue.click()
        inp_password = await browser.find_element(By.ID, "password", timeout=TIMEOUT)
        await inp_password.send_keys(SPOT_PS)
        btn_next = await browser.find_element(By.ID, "next", timeout=TIMEOUT)
        await btn_next.click()
        await browser.sleep(3)
        await browser.get(SPOT_URL, wait_load=True)
        drop_zones = await browser.find_element(
            By.CSS_SELECTOR, "#parking-spot-zones > div > div > a", timeout=TIMEOUT
        )
        await drop_zones.click()
        await browser.sleep(1)
        li_zones = await browser.find_elements(
            By.CSS_SELECTOR, "#parking-spot-zones > div > div > ul > li > a"
        )
        for zone in li_zones:
            text = await zone.text
            if "katowice face2face b" in text.lower():
                li_F2FB = zone
                await li_F2FB.click()
                break

        await browser.sleep(3)

        booked_spot = False
        while not booked_spot:
            col_day_to_take = await browser.find_element(
                By.CSS,
                f"#day-to-take-{TARGET_DATE} > div.list__item-col.text-right",
                timeout=TIMEOUT,
            )
            text_day_to_take = await col_day_to_take.text

            if "is yours" in text_day_to_take.lower():
                print("You already have a spot!")
                booked_spot = True
            elif "free spots: 0" in text_day_to_take.lower():
                print("No free spots... Awaiting and refreshing...")
                await browser.sleep(10)
                await browser.refresh()
            elif "on waiting list" in text_day_to_take.lower():
                print("Waiting list still not cleared...")
                dt_now = dt.now()
                dt_target = dt.today().replace(hour=19, minute=00, second=00)
                t_wait = dt_target - dt_now
                if t_wait.seconds > 180:
                    print("Waiting 3 minutes...")
                    await browser.sleep(180)
                elif t_wait.seconds < 180 and t_wait.seconds > 0:
                    print("Waiting {t_wait.seconds} seconds...")
                    await browser.sleep(t_wait.seconds)
                else:
                    print("Still not cleared...")
                    await browser.sleep(2)
                print("Refresh...")
                await browser.refresh()
            else:
                print("Attempting to book a spot...")
                btn_book_any = await browser.find_element(
                    By.CSS, f"#take-{TARGET_DATE}", timeout=TIMEOUT
                )
                await btn_book_any.click(scroll_to=True, move_to=True)
                await browser.sleep(5)
                await browser.refresh()


if __name__ == "__main__":
    asyncio.run(main())
