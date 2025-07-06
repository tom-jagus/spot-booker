import os
from dotenv import load_dotenv
from datetime import datetime as dt
from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio

load_dotenv()

TIMEOUT = 10
SPOT_URL = os.getenv("SPOT_URL")
SPOT_UN = os.getenv("SPOT_UN")
SPOT_PS = os.getenv("SPOT_PS")
TODAY = dt.today()


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

        available_zones = []

        for n, zone in enumerate(li_zones, 0):
            zone_text = await zone.text
            zone_text = zone_text.strip()
            
            available_zones.append(zone_text)
            print(n, zone_text)


        user_selection = input("Select a parking zone: ")
        selected_zone = available_zones[int(user_selection)]

        for zone in li_zones:
            text = await zone.text
            if selected_zone in text:
                li_selected = zone
                await li_selected.click()
                break

        await browser.sleep(3)

        target_day = int(input("Select day to target. Today (0) or Tomorrow (1): "))
        TARGET_DATE = f"{(TODAY.day + target_day):02}-{TODAY.month:02}"
        print(TARGET_DATE)

        print("Please deal with Recaptcha prompt...")
        input("Press ENTER to continue...")


        
        # # Human verification
        # try:
        #     booker = await browser.find_element(
        #             By.CSS, f"#take-{TODAY.day}-{TODAY.month:02}", timeout=TIMEOUT
        #         )
        #     await booker.click(scroll_to=True, move_to=True)
        #     await browser.sleep(2)
        #
        #     # await browser.find_element(By.CSS_SELECTOR, "#parkanizer-offices-app > ux-dialog-container > div > div > ux-dialog > ux-dialog-body > h1", timeout=5)
        #     human_verification_box = await browser.find_element(By.CSS_SELECTOR, "#rc-anchor-container", timeout=5)
        #     await human_verification_box.click()
        #     try:
        #         picture_verification = await browser.find_element(By.CSS_SELECTOR, "#parkanizer-offices-app > div:nth-child(5) > div:nth-child(4) > iframe", timeout=5)
        #         browser.refresh()
        #     except:
        #         pass
        # except:
        #     pass
        #
        # print("waiting...")
        # await browser.sleep(10000)

        await browser.get(SPOT_URL, wait_load=True)

        booked_spot = False
        attempts_counter = 0
        while not booked_spot:
            attempts_counter += 1
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
                print(f"Attempt {attempts_counter}. No free spots... Awaiting and refreshing...")
                await browser.sleep(10)
                await browser.refresh()
            elif "on waiting list" in text_day_to_take.lower():
                print("Waiting list still not cleared...")
                attempts_counter -= 1
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
                await browser.sleep(2)
                try:
                    print("Trying")
                    human_verification = await browser.find_element(By.CSS, "#parkanizer-offices-app > ux-dialog-container > div > div > ux-dialog > ux-dialog-body > h1", timeout=2)
                    if "Human Verification" in await human_verification.text:
                        input("Deal with recaptcha... Again...")
                except:
                    pass

                await browser.refresh()


if __name__ == "__main__":
    asyncio.run(main())
