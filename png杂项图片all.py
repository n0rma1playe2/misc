import subprocess
import re
import zlib
import binascii
import struct
import shutil
import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="CTF Misc 图片隐写All in One工具")
    parser.add_argument("image_path", help="输入图片路径")
    parser.add_argument("-p", "--password", help="可能用于解密的密钥（可选）", required=False)
    return parser.parse_args()

def run_command(command):
    result = subprocess.run(command, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True,
                            errors='ignore'
                            )
    return result

def exiftool(image_path):
    command = f'exiftool {image_path}'
    result = run_command(command)

    try:
        xp_comment = re.search(r'XP Comment\s+:\s+(.+)', result.stdout).group(1)
    except:
        xp_comment = None

    if xp_comment:
        print("[+]exiftool: %s" % xp_comment)
    else:
        print("[-]exiftool: 未找到内容")

def zsteg(image_path):

    text_pattern = r"flag\{.*?\}|flag|666c6167|f1ag|fl4g|Zmxh|&#102;MZWGC|102 108 97 103|1100110|ctf|ctf\{.*?\}|key|464C4147|pass|{|}"
    file_patterns = {
        'PNG': (r'PNG image data', 'png'),
        'JPG': (r'JPEG image data', 'jpg'),
        'ZIP': (r'Zip archive data', 'zip'),
        'RAR': (r'RAR archive data', 'rar'),
        '7z': (r'7-zip archive data', '7z')
    }

    command = f'zsteg -a {image_path}'
    result = run_command(command)
    stdout_lines = result.stdout.splitlines()

    combined_results = []

    for line in stdout_lines:
        if re.search(text_pattern, line):
            print(f"[+]zsteg: {line}")
            combined_results.append(line)

    file_matches = re.findall(r'(b\d,\w+,\w+,\w+)\s+.. file:\s+(.+)', result.stdout)
    
    if file_matches:
        for match in file_matches:
            channel = match[0]
            file_description = match[1]
            
            for fmt, (fmt_pattern, extension) in file_patterns.items():
                if re.search(fmt_pattern, file_description):
                    output_dir = './zsteg'
                    os.makedirs(output_dir, exist_ok=True)

                    output_file = os.path.join(output_dir, f"output.{extension}")
                    extract_command = f"zsteg -e {channel} {image_path} > {output_file}"

                    subprocess.run(extract_command, shell=True)

                    print(f"[+]zsteg: 识别到文件, 已自动保存到 {output_file}")
                    combined_results.append(f"{channel} : {file_description} -> {output_file}")
                    break

def CRC_Crack(image_path, image_name):
    
    with open(image_path, 'rb') as image_data:
        bin_data = image_data.read()

    crc32key = zlib.crc32(bin_data[12:29])
    stored_crc32key = int(bin_data[29:33].hex(), 16)

    if crc32key == stored_crc32key:
        print('[-]CRC宽高爆破: 宽高没有问题')
        return

    fr = bytearray(bin_data)

    data = bytearray(fr[0x0c:0x1d])
    crc32key = int.from_bytes(fr[0x1d:0x21], byteorder='big')

    n = 4095
    for w in range(n):
        width = bytearray(struct.pack('>i', w))
        for h in range(n):
            height = bytearray(struct.pack('>i', h))
            for x in range(4):
                data[x + 4] = width[x]
                data[x + 8] = height[x]

            crc32result = binascii.crc32(data) & 0xffffffff

            if crc32result == crc32key:
                for x in range(4):
                    fr[x + 16] = width[x]
                    fr[x + 20] = height[x]

                output_dir = './CRC_Crack/'
                os.makedirs(output_dir, exist_ok=True)

                output_file = os.path.join(output_dir, f'fix_{image_name}')
                with open(output_file, 'wb') as fw:
                    fw.write(fr)

                print(f'[+]CRC宽高爆破: 爆破成功, 文件已保存至 {output_file}')
                return

    print('[-]CRC宽高爆破: 非png文件, 爆破失败')

def foremost(image_path):
    output_dir = './foremost'
    command = f'foremost -i {image_path} -o {output_dir}'
    run_command(command)

    file_count = 0
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file != 'audit.txt':
                file_count += 1
    if file_count >= 2:
        print("[+]foremost: 提取成功，文件已保存至foremost目录")
    else:
        print("[-]foremost: 未找到内容")
        shutil.rmtree(output_dir)

def strings_check(image_path):

    pattern = r"flag\{.*?\}|flag|666c6167|f1ag|fl4g|Zmxh|&#102;MZWGC|102 108 97 103|1100110|ctf|ctf\{.*?\}|key|464C4147|pass"
    regex = re.compile(pattern)

    command = f'strings {image_path}'
    result = run_command(command)

    output = result.stdout.splitlines()
    match_found = False

    for line in output:

        if regex.search(line):
            print(f"[+]strings: {line}")
            match_found = True
    if not match_found:
        print("[-]strings: 未找到内容")

def F5_steganography(image_path, password):

    output_dir = './F5-steganography'
    os.makedirs(output_dir, exist_ok=True)
    tool_path = os.path.expanduser('~/tools/F5-steganography/')

    if password:
        command = f'java -cp {tool_path} Extract {image_path} -p {password}'
    else:
        command = f'java -cp {tool_path} Extract {image_path}'

    result = run_command(command)

    if result.returncode == 0:

        extracted_file = 'output.txt'
        if os.path.exists(extracted_file):
            target_path = os.path.join(output_dir, 'output.txt')
            shutil.move(extracted_file, target_path)
            print(f"[+]F5-steganography: 提取成功, 文件已保存至 {target_path}")

    else:
        print("[-] F5-steganography: 内容未找到")

# def steghide(image_path, password, wordlist_path):
    
#         output_dir = './steghide'
#         os.makedirs(output_dir, exist_ok=True)
    
#         if password:
#             command = f'steghide extract -sf {image_path} -p {password} -xf {output_dir}'
#             result = run_command(command)



#         else:
#             stegseek()


# def stegseek():
#     command = 'stegseek {image_path} /usr/share/wordlists/rockyou.txt'
#     result = run_command(command)
#     if result.returncode == 0:
#         print(f"[+]stegseek: 提取成功, 密码为 {result.stdout}")
#     else:
#         print("[-]stegseek: 内容未找到")

def main():
    args = parse_args()
    image_path = args.image_path
    image_name = image_path.split('/')[-1]
    password = args.password

    exiftool(image_path)
    strings_check(image_path)
    zsteg(image_path)
    CRC_Crack(image_path, image_name)
    foremost(image_path)
    F5_steganography(image_path, password)

if __name__ == '__main__':
    main()
