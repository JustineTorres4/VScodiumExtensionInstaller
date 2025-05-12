import sys
sys.path.insert(0, './lib')
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
import time
import subprocess
import os

def extract_extension_info(driver, url):
    driver.get(url)
    time.sleep(2)

    try:
        command_input = driver.find_element(By.ID, "vscode-command-input")
        install_command = command_input.get_attribute("value")
        extension_name = install_command.replace("ext install ", "").strip()
    except:
        return url, None, None

    try:
        version_tab = driver.find_element(By.ID, "versionHistory")
        version_tab.click()
        time.sleep(2)
        version_table = driver.find_element(By.CLASS_NAME, "version-history-table-body")
        first_row = version_table.find_elements(By.CLASS_NAME, "version-history-container-row")[0]
        version = first_row.find_elements(By.CLASS_NAME, "version-history-container-column")[0].text.strip()
    except:
        version = None

    return url, extension_name, version

def main(file_path):
    print("Select your platform:")
    print("1 - Alpine Linux 64 bit     alpine-x64")
    print("2 - Alpine Linux ARM64      alpine-arm64")
    print("3 - Linux ARM32             linux-armhf")
    print("4 - Linux ARM64             linux-arm64")
    print("5 - Linux x64               linux-x64")
    print("6 - Windows ARM             win32-arm64")
    print("7 - Windows x64             win32-x64")
    print("8 - macOS Apple Silicon     darwin-arm64")
    print("9 - macOS Intel             darwin-x64")
    platform_choice = input("Enter platform number (1-9): ").strip()

    platforms = {
        "1": "alpine-x64",
        "2": "alpine-arm64",
        "3": "linux-armhf",
        "4": "linux-arm64",
        "5": "linux-x64",
        "6": "win32-arm64",
        "7": "win32-x64",
        "8": "darwin-arm64",
        "9": "darwin-x64"
    }
    target_platform = platforms.get(platform_choice, "")
    platform_arg = platform_choice if platform_choice in platforms else ""

    #Selenium
    options = FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")

    project_driver = os.path.join(os.getcwd(), "driver", "geckodriver")
    if os.path.isfile(project_driver) and os.access(project_driver, os.X_OK):
        print(f"Using local geckodriver at {project_driver} :)")
        service = FirefoxService(executable_path=project_driver)
    else:
        print("⚠️ Local geckodriver not found or not executable, downloading via GeckoDriverManager")
        path = GeckoDriverManager().install()
        service = FirefoxService(path)
    driver = webdriver.Firefox(service=service, options=options)

    with open(file_path, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    output_lines = []

    for url in urls:
        _, name, version = extract_extension_info(driver, url)
        if name and version:
            line = f"{name}.{version}"
            print(line)
            output_lines.append(line)
        else:
            print(f"⚠️ Failed to extract info from: {url}")

    driver.quit()

    with open("extensions.txt", "w") as out:
        out.write("\n".join(output_lines))

    installer_script = "./extensionInstaller.sh"
    if not os.access(installer_script, os.X_OK):
        print(f"❗ {installer_script} is not executable. Run: chmod +x extensionInstaller")
    else:
        for line in output_lines:
            if platform_arg:
                print(f"📦 Installing: {line} (platform #{platform_arg} → {target_platform})")
                subprocess.run([installer_script, line, platform_arg])
            else:
                print(f"📦 Installing: {line}")
                subprocess.run([installer_script, line])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("⚠️ Usage: python vs_extension_info_batch.py urls.txt")
        sys.exit(1)
    main(sys.argv[1])
