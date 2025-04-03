import os
import shutil
import subprocess


class PolSARpro:
    soft_path = ""          # 软件路径
    input_dir = ""          # 输入目录
    output_dir = ""         # 输出目录
    pol_format = ""         # 极化格式
    row_offset = 0          # 行偏移量
    col_offset = 0          # 列偏移量
    row_final = 0           # 处理到多少行
    col_final = 0           # 处理到多少列
    mask_file = ""          # 掩膜文件
    root_dir = ""           # 数据集根目录

    def __init__(self, soft_path, input_dir, output_dir, pol_format, row_offset, col_offset, row_final, col_final):
        self.soft_path = soft_path
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.pol_format = pol_format
        self.row_offset = row_offset
        self.col_offset = col_offset
        self.row_final = row_final
        self.col_final = col_final
        self.mask_file = os.path.join(self.input_dir, "mask_valid_pixels.bin")
        if not os.path.exists(os.path.join(self.input_dir, "mask_valid_pixels.bin")):
            self.create_mask_valid_pixels()
            self.create_bmp_file(os.path.join(self.input_dir, "mask_valid_pixels.bin"), os.path.join(self.input_dir, "mask_valid_pixels.bmp"), "float", "real", "jet", 0, 0, 1, "black")
        if pol_format == "S2":
            self.root_dir = input_dir
        else:
            self.root_dir = os.path.abspath(os.path.join(input_dir, os.pardir))

    def create_mask_valid_pixels(self):
        program_path = os.path.join(self.soft_path, "tools", "create_mask_valid_pixels.exe")
        command = [
            program_path,
            "-id", self.input_dir,
            "-od", self.output_dir,
            "-idf", self.pol_format,    # "S2", "C2", "C3","C4", "T3", "T4", "T6", "SPP", "IPP"
            "-ofr", str(self.row_offset),
            "-ofc", str(self.col_offset),
            "-fnr", str(self.row_final),
            "-fnc", str(self.col_final)
        ]
        subprocess.run(command)
        self.mask_file = os.path.join(self.output_dir, "mask_valid_pixels.bin")

    def create_bmp_file(self, input_file, output_file, input_format, output_format, colormap, min_max_auto, min_val, max_val, mask_file_color):
        program_path = os.path.join(self.soft_path, "bmp_process", "create_bmp_file.exe")
        command = [
            program_path,
            "-if", input_file,
            "-of", output_file,
            "-ift", input_format,                            # 输入数据格式 (cmplx, float, int)
            "-oft", output_format,                           # 输出数据格式 (real, imag, mod, pha, db10, db20）
            "-clm", colormap,                                # colormap (gray, grayrev, jet, jetinv, jetrev, hsv, hsvinv, hsvrev)
            "-nc", str(self.col_final - self.col_offset),
            "-ofr", str(self.row_offset),
            "-ofc", str(self.col_offset),
            "-fnr", str(self.row_final),
            "-fnc", str(self.col_final),
            "-mm", str(min_max_auto),                        # 自动确定min, max (0, 1, 2, 3) 0为自动
            "-min", str(min_val),
            "-max", str(max_val),
            "-mask", self.mask_file,
            "-mcol", mask_file_color                         # mask file color (white, gray, black)
        ]
        subprocess.run(command)

    def create_pauli_rgb_file(self, input_dir, output_file, min_max_auto, blue_min, blue_max, red_min, red_max, green_min, green_max):
        program_path = os.path.join(self.soft_path, "bmp_process", "create_pauli_rgb_file.exe")
        command = [
            program_path,
            "-id", input_dir,
            "-of", output_file,
            "-iodf", self.pol_format,    # "S2", "C3", "T3", "C4", "T4"
            "-ofr", str(self.row_offset),
            "-ofc", str(self.col_offset),
            "-fnr", str(self.row_final),
            "-fnc", str(self.col_final),
            "-auto", str(min_max_auto),
            "-minb", str(blue_min),
            "-maxb", str(blue_max),
            "-minr", str(red_min),
            "-maxr", str(red_max),
            "-ming", str(green_min),
            "-maxg", str(green_max),
            "-mask", self.mask_file
        ]
        subprocess.run(command)

    def create_rgb_file(self, blue_file, red_file, green_file, output_file, min_max_auto, blue_min, blue_max, red_min, red_max, green_min, green_max):
        program_path = os.path.join(self.soft_path, "bmp_process", "create_rgb_file.exe")
        command = [
            program_path,
            "-ifb", blue_file,
            "-ifr", red_file,
            "-ifg", green_file,
            "-of", output_file,
            "-inc", str(self.col_final-self.col_offset),
            "-ofr", str(self.row_offset),
            "-ofc", str(self.col_offset),
            "-fnr", str(self.row_final),
            "-fnc", str(self.col_final),
            "-auto", str(min_max_auto),
            "-minb", str(blue_min),
            "-maxb", str(blue_max),
            "-minr", str(red_min),
            "-maxr", str(red_max),
            "-ming", str(green_min),
            "-maxg", str(green_max),
            "-mask", self.mask_file
        ]
        subprocess.run(command)

    def an_yang_filter(self, input_output_format, num_looks, k_coefficient, patch_window_size_row, patch_window_size_col, searching_window_size_row, searching_window_size_col):
        if len(input_output_format) != 4:
            new_dir = os.path.abspath(os.path.join(self.root_dir, os.path.pardir, os.path.basename(self.root_dir) + "_PRE", self.pol_format))
            self.root_dir = new_dir
        else:
            new_dir = os.path.abspath(os.path.join(self.root_dir, os.path.pardir, os.path.basename(self.root_dir) + "_PRE", input_output_format[-2:]))
            self.root_dir = os.path.abspath(os.path.join(new_dir, os.path.pardir))
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        program_path = os.path.join(self.soft_path, "speckle_filter", "an_yang_filter.exe")
        command = [
            program_path,
            "-id", self.input_dir,
            "-od", new_dir,
            "-iodf", input_output_format,              # 输入-输出格式（单格式代表输入输出格式相同） "S2C3", "S2C4", "S2T3", "S2T4", "C2", "C3", "C4", "T2", "T3", "T4", "SPP", "IPP"
            "-ofr", str(self.row_offset),
            "-ofc", str(self.col_offset),
            "-fnr", str(self.row_final),
            "-fnc", str(self.col_final),
            "-nlk", str(num_looks),                    # 多视
            "-k", str(k_coefficient),                  # k参数
            "-nwr", str(patch_window_size_row),        # 补丁窗口行大小
            "-nwc", str(patch_window_size_col),        # 补丁窗口列大小
            "-swr", str(searching_window_size_row),    # 搜索窗口行大小
            "-swc", str(searching_window_size_col),    # 搜索窗口列大小
            "-mask", self.mask_file
        ]
        subprocess.run(command)
        shutil.copy(os.path.join(self.input_dir, "config.txt"), os.path.join(new_dir, "config.txt"))
        self.input_dir = new_dir
        self.output_dir = new_dir
        if len(input_output_format) == 4:
            self.pol_format = input_output_format[-2:]
        self.create_mask_valid_pixels()
        self.mask_file = os.path.join(new_dir, "mask_valid_pixels.bin")
        self.create_bmp_file(self.mask_file, os.path.join(self.output_dir, "mask_valid_pixels.bmp"), "float", "real", "jet", 0, 0, 1, "black")

    def lee_refined_filter(self, input_output_format, num_looks, window_size):
        if len(input_output_format) != 4:
            new_dir = os.path.abspath(os.path.join(self.root_dir, os.path.pardir, os.path.basename(self.root_dir) + "_LEE", self.pol_format))
            self.root_dir = new_dir
        else:
            new_dir = os.path.abspath(os.path.join(self.root_dir, os.path.pardir, os.path.basename(self.root_dir) + "_LEE", input_output_format[-2:]))
            self.root_dir = os.path.abspath(os.path.join(new_dir, os.path.pardir))
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        program_path = os.path.join(self.soft_path, "speckle_filter", "lee_refined_filter.exe")
        command = [
            program_path,
            "-id", self.input_dir,
            "-od", new_dir,
            "-iodf", input_output_format,    # "S2C3", "S2C4", "S2T3", "S2T4", "C2", "C3", "C4", "T2", "T3", "T4", "SPP", "IPP"
            "-ofr", str(self.row_offset),
            "-ofc", str(self.col_offset),
            "-fnr", str(self.row_final),
            "-fnc", str(self.col_final),
            "-nlk", str(num_looks),
            "-nw", str(window_size),         # 窗口大小
            "-mask", self.mask_file
        ]
        subprocess.run(command)
        shutil.copy(os.path.join(self.input_dir, "config.txt"), os.path.join(new_dir, "config.txt"))
        self.input_dir = new_dir
        self.output_dir = new_dir
        if len(input_output_format) == 4:
            self.pol_format = input_output_format[-2:]
        self.create_mask_valid_pixels()
        self.mask_file = os.path.join(new_dir, "mask_valid_pixels.bin")
        self.create_bmp_file(self.mask_file, os.path.join(self.output_dir, "mask_valid_pixels.bmp"), "float", "real", "jet", 0, 0, 1, "black")

    def h_a_alpha_decomposition(self, flag_parameters, flag_h_a_alpha, flag_comb_ha, flag_comb_h1ma, flag_comb_1mha, flag_comb_1mh1ma, window_size_row, window_size_col):
        if self.pol_format == "S2":
            input_output_format = "S2T3"    # 虽然源代码中有"S2T3", "S2C3", "S2T4", "S2C4"这几个参数，但是实际使用PolSARpro时并没有选择输出格式的选项，而是默认使用"S2T3"，并且也不会输出转换的数据文件
        else:
            input_output_format = self.pol_format
        if flag_h_a_alpha == 1:
            flag_alpha = 1
            flag_entropy = 1
            flag_anisotropy = 1
        else:
            flag_alpha = 0
            flag_entropy = 0
            flag_anisotropy = 0
        flag_lambda = 0
        program_path = os.path.join(self.soft_path, "data_process_sngl", "h_a_alpha_decomposition.exe")
        command = [
            program_path,
            "-id", self.input_dir,
            "-od", self.output_dir,
            "-iodf", input_output_format,    # "S2T3", "S2C3", "S2T4", "S2C4", "SPPC2", "C2", "C3", "C3T3", "C4", "C4T4", "T3", "T4"
            "-ofr", str(self.row_offset),
            "-ofc", str(self.col_offset),
            "-fnr", str(self.row_final),
            "-fnc", str(self.col_final),
            "-fl1", str(flag_parameters),
            "-fl2", str(flag_lambda),
            "-fl3", str(flag_alpha),
            "-fl4", str(flag_entropy),
            "-fl5", str(flag_anisotropy),
            "-fl6", str(flag_comb_ha),
            "-fl7", str(flag_comb_h1ma),
            "-fl8", str(flag_comb_1mha),
            "-fl9", str(flag_comb_1mh1ma),
            "-nwr", str(window_size_row),
            "-nwc", str(window_size_col),
            "-mask", self.mask_file
        ]
        subprocess.run(command)
        if flag_parameters == 1:
            self.create_bmp_file(os.path.join(self.output_dir, "alpha.bin"), os.path.join(self.output_dir, "alpha.bmp"), "float", "real", "jet", 0, 0, 1, "black")
            self.create_bmp_file(os.path.join(self.output_dir, "beta.bin"), os.path.join(self.output_dir, "beta.bmp"), "float", "real", "jet", 0, 0, 1, "black")
            self.create_bmp_file(os.path.join(self.output_dir, "delta.bin"), os.path.join(self.output_dir, "delta.bmp"), "float", "real", "hsv", 0, 0, 1, "black")
            self.create_bmp_file(os.path.join(self.output_dir, "gamma.bin"), os.path.join(self.output_dir, "gamma.bmp"), "float", "real", "hsv", 0, 0, 1, "black")
            self.create_bmp_file(os.path.join(self.output_dir, "lambda.bin"), os.path.join(self.output_dir, "lambda_db.bmp"), "float", "db10", "gray", 1, 0, 1, "black")
        if flag_h_a_alpha == 1:
            self.create_bmp_file(os.path.join(self.output_dir, "alpha.bin"), os.path.join(self.output_dir, "alpha.bmp"), "float", "real", "jet", 0, 0, 1, "black")
            self.create_bmp_file(os.path.join(self.output_dir, "entropy.bin"), os.path.join(self.output_dir, "entropy.bmp"), "float", "real", "jet", 0, 0, 1, "black")
            self.create_bmp_file(os.path.join(self.output_dir, "anisotropy.bin"), os.path.join(self.output_dir, "anisotropy.bmp"), "float", "real", "jet", 0, 0, 1, "black")
        if flag_comb_ha == 1:
            self.create_bmp_file(os.path.join(self.output_dir, "combination_HA.bin"), os.path.join(self.output_dir, "combination_HA.bmp"), "float", "real", "jet", 0, 0, 1, "black")
        if flag_comb_h1ma == 1:
            self.create_bmp_file(os.path.join(self.output_dir, "combination_H1mA.bin"), os.path.join(self.output_dir, "combination_H1mA.bmp"), "float", "real", "jet", 0, 0, 1, "black")
        if flag_comb_1mha == 1:
            self.create_bmp_file(os.path.join(self.output_dir, "combination_1mHA.bin"), os.path.join(self.output_dir, "combination_1mHA.bmp"), "float", "real", "jet", 0, 0, 1, "black")
        if flag_comb_1mh1ma == 1:
            self.create_bmp_file(os.path.join(self.output_dir, "combination_1mH1mA.bin"), os.path.join(self.output_dir, "combination_1mH1mA.bmp"), "float", "real", "jet", 0, 0, 1, "black")

    def yamaguchi_4components_decomposition(self, mode, window_size_row, window_size_col):
        program_path = os.path.join(self.soft_path, "data_process_sngl", "yamaguchi_4components_decomposition.exe")
        command = [
            program_path,
            "-id", self.input_dir,
            "-od", self.output_dir,
            "-iodf", self.pol_format,      # "S2", "C3", "T3"
            "-ofr", str(self.row_offset),
            "-ofc", str(self.col_offset),
            "-fnr", str(self.row_final),
            "-fnc", str(self.col_final),
            "-mod", mode,                  # 分解模式 "Y4O", "Y4R", "S4R"
            "-nwr", str(window_size_row),
            "-nwc", str(window_size_col),
            "-mask", self.mask_file
        ]
        subprocess.run(command)
        input_files = ["Yamaguchi4_"+mode+"_Odd.bin", "Yamaguchi4_"+mode+"_Dbl.bin", "Yamaguchi4_"+mode+"_Vol.bin", "Yamaguchi4_"+mode+"_Hlx.bin"]
        for input_file in input_files:
            self.create_bmp_file(os.path.join(self.output_dir, input_file), os.path.join(self.output_dir, f"{os.path.splitext(input_file)[0]}_db.bmp"), "float", "db10", "gray", 1, 0, 1, "black")
        self.create_rgb_file(os.path.join(self.output_dir, input_files[0]), os.path.join(self.output_dir, input_files[1]), os.path.join(self.output_dir, input_files[2]), os.path.join(self.output_dir, "Yamaguchi4_"+mode+"_RGB.bmp"), 1, 0, 0, 0, 0, 0, 0)

    def huynen_decomposition(self, input_output_format, window_size_row, window_size_col):
        if len(input_output_format) != 4:
            new_dir = os.path.abspath(os.path.join(self.root_dir, os.path.pardir, os.path.basename(self.root_dir) + "_JRH", self.pol_format))
            self.root_dir = new_dir
        else:
            new_dir = os.path.abspath(os.path.join(self.root_dir, os.path.pardir, os.path.basename(self.root_dir) + "_JRH", input_output_format[-2:]))
            self.root_dir = os.path.abspath(os.path.join(new_dir, os.path.pardir))
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        program_path = os.path.join(self.soft_path, "data_process_sngl", "huynen_decomposition.exe")
        command = [
            program_path,
            "-id", self.input_dir,
            "-od", new_dir,
            "-iodf", input_output_format,    # "S2C3", "S2T3", "C3", "T3"
            "-ofr", str(self.row_offset),
            "-ofc", str(self.col_offset),
            "-fnr", str(self.row_final),
            "-fnc", str(self.col_final),
            "-nwr", str(window_size_row),
            "-nwc", str(window_size_col),
            "-mask", self.mask_file
        ]
        subprocess.run(command)
        shutil.copy(os.path.join(self.input_dir, "config.txt"), os.path.join(new_dir, "config.txt"))
        if input_output_format[-2:] == "C3":
            input_files = ["C11.bin", "C22.bin", "C33.bin"]
            new_pol_format = "C3"
        else:
            input_files = ["T11.bin", "T22.bin", "T33.bin"]
            new_pol_format = "T3"
        for input_file in input_files:
            if len(input_output_format) == 4:
                self.create_bmp_file(os.path.join(new_dir, input_file), os.path.join(self.input_dir, new_pol_format, f"Huynen_{os.path.splitext(input_file)[0]}_dB.bmp"), "float", "db10", "gray", 1, 0, 0, "black")
            else:
                self.create_bmp_file(os.path.join(new_dir, input_file), os.path.join(self.input_dir, f"Huynen_{os.path.splitext(input_file)[0]}_dB.bmp"), "float", "db10", "gray", 1, 0, 0, "black")
        self.create_pauli_rgb_file(new_dir, os.path.join(self.input_dir, "Huynen_RGB.bmp"), 1, 0, 0, 0, 0, 0, 0)

    def krogager_decomposition(self, window_size_row, window_size_col):
        program_path = os.path.join(self.soft_path, "data_process_sngl", "krogager_decomposition.exe")
        command = [
            program_path,
            "-id", self.input_dir,
            "-od", self.output_dir,
            "-iodf", self.pol_format,    # "S2", "C3", "T3"
            "-ofr", str(self.row_offset),
            "-ofc", str(self.col_offset),
            "-fnr", str(self.row_final),
            "-fnc", str(self.col_final),
            "-nwr", str(window_size_row),
            "-nwc", str(window_size_col),
            "-mask", self.mask_file
        ]
        subprocess.run(command)
        input_files = ["Krogager_Ks.bin", "Krogager_Kd.bin", "Krogager_Kh.bin"]
        for input_file in input_files:
            self.create_bmp_file(os.path.join(self.output_dir, input_file), os.path.join(self.output_dir, f"{os.path.splitext(input_file)[0]}_dB.bmp"), "float", "db10", "gray", 1, 0, 0, "black")
        self.create_rgb_file(os.path.join(self.output_dir, input_files[0]), os.path.join(self.output_dir, input_files[1]), os.path.join(self.output_dir, input_files[2]), os.path.join(self.output_dir, "Krogager_RGB.bmp"), 1, 0, 0, 0, 0, 0, 0)

    def cloude_decomposition(self, input_output_format, window_size_row, window_size_col):
        if len(input_output_format) != 4:
            new_dir = os.path.abspath(os.path.join(self.root_dir, os.path.pardir, os.path.basename(self.root_dir) + "_SRC", self.pol_format))
            self.root_dir = new_dir
        else:
            new_dir = os.path.abspath(os.path.join(self.root_dir, os.path.pardir, os.path.basename(self.root_dir) + "_SRC", input_output_format[-2:]))
            self.root_dir = os.path.abspath(os.path.join(new_dir, os.path.pardir))
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        program_path = os.path.join(self.soft_path, "data_process_sngl", "cloude_decomposition.exe")
        command = [
            program_path,
            "-id", self.input_dir,
            "-od", new_dir,
            "-iodf", input_output_format,    # "S2C3", "S2T3", "C3", "T3"
            "-ofr", str(self.row_offset),
            "-ofc", str(self.col_offset),
            "-fnr", str(self.row_final),
            "-fnc", str(self.col_final),
            "-nwr", str(window_size_row),
            "-nwc", str(window_size_col),
            "-mask", self.mask_file
        ]
        subprocess.run(command)
        shutil.copy(os.path.join(self.input_dir, "config.txt"), os.path.join(new_dir, "config.txt"))
        if input_output_format[-2:] == "C3":
            input_files = ["C11.bin", "C22.bin", "C33.bin"]
            new_pol_format = "C3"
        else:
            input_files = ["T11.bin", "T22.bin", "T33.bin"]
            new_pol_format = "T3"
        for input_file in input_files:
            if len(input_output_format) == 4:
                self.create_bmp_file(os.path.join(new_dir, input_file), os.path.join(self.input_dir, new_pol_format, f"Cloude_{os.path.splitext(input_file)[0]}_dB.bmp"), "float", "db10", "gray", 1, 0, 0, "black")
            else:
                self.create_bmp_file(os.path.join(new_dir, input_file), os.path.join(self.input_dir, f"Cloude_{os.path.splitext(input_file)[0]}_dB.bmp"), "float", "db10", "gray", 1, 0, 0, "black")
        self.create_pauli_rgb_file(new_dir, os.path.join(self.input_dir, "Cloude_RGB.bmp"), 1, 0, 0, 0, 0, 0, 0)

    def process_elements(self, element_index, process_format):
        program_path = os.path.join(self.soft_path, "data_process_sngl", "process_elements.exe")
        command = [
            program_path,
            "-id", self.input_dir,
            "-od", self.output_dir,
            "-iodf", self.pol_format,      # "S2", "C3", "T3", "SPP", "IPP"
            "-ofr", str(self.row_offset),
            "-ofc", str(self.col_offset),
            "-fnr", str(self.row_final),
            "-fnc", str(self.col_final),
            "-elt", str(element_index),    # 矩阵元素下标
            "-fmt", process_format,        # S2, SPP, IPP: A, Adb, I, Idb, pha    C3, T3: mod, db, pha
            "-mask", self.mask_file
        ]
        subprocess.run(command)
        if process_format == "A":
            file_name = "A" + element_index
        elif process_format == "I":
            file_name = "I" + element_index
        elif process_format in ("Idb", "db"):
            file_name = self.pol_format[0] + element_index + "_db"
        elif process_format == "pha":
            file_name = self.pol_format[0] + element_index + "_pha"
        else:
            file_name = self.pol_format[0] + element_index + "_mod"
        if process_format == "pha":
            self.create_bmp_file(os.path.join(self.output_dir, file_name + ".bin"), os.path.join(self.output_dir, file_name + ".bmp"), "float", "real", "hsv", 0, -180, 180, "black")
        else:
            self.create_bmp_file(os.path.join(self.output_dir, file_name + ".bin"), os.path.join(self.output_dir, file_name + ".bmp"), "float", "real", "gray", 1, 0, 0, "black")

    def process_corr(self, element_index, window_size_row, window_size_col):
        program_path = os.path.join(self.soft_path, "data_process_sngl", "process_corr.exe")
        command = [
            program_path,
            "-id", self.input_dir,
            "-od", self.output_dir,
            "-iodf", self.pol_format,    # "S2m", "S2b", "C2", "C3", "C4", "T3", "T4", "SPP"
            "-ofr", str(self.row_offset),
            "-ofc", str(self.col_offset),
            "-fnr", str(self.row_final),
            "-fnc", str(self.col_final),
            "-elt", str(element_index),
            "-nwr", str(window_size_row),
            "-nwc", str(window_size_col),
            "-mask", self.mask_file
        ]
        subprocess.run(command)
        self.create_bmp_file(os.path.join(self.output_dir, "Ro"+element_index+".bin"), os.path.join(self.output_dir, "Ro"+element_index+"_mod.bmp"), "cmplx", "mod", "jet", 0, 0, 1, "black")
        self.create_bmp_file(os.path.join(self.output_dir, "Ro"+element_index+".bin"), os.path.join(self.output_dir, "Ro"+element_index+"_pha.bmp"), "cmplx", "pha", "hsv", 0, -180, 180, "black")

    def orientation_compensation(self, window_size_row, window_size_col):
        if self.pol_format == "S2":
            new_dir = os.path.abspath(os.path.join(self.root_dir, os.path.pardir, os.path.basename(self.root_dir) + "_POC"))
            self.root_dir = new_dir
        else:
            new_dir = os.path.abspath(os.path.join(self.root_dir, os.path.pardir, os.path.basename(self.root_dir) + "_POC", self.pol_format))
            self.root_dir = os.path.abspath(os.path.join(new_dir, os.path.pardir))
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        program_path = os.path.join(self.soft_path, "data_process_sngl", "orientation_estimation.exe")
        command = [
            program_path,
            "-id", self.input_dir,
            "-od", new_dir,
            "-iodf", self.pol_format,    # "S2", "C3", "T3"
            "-ofr", str(self.row_offset),
            "-ofc", str(self.col_offset),
            "-fnr", str(self.row_final),
            "-fnc", str(self.col_final),
            "-nwr", str(window_size_row),
            "-nwc", str(window_size_col),
            "-mask", self.mask_file
        ]
        subprocess.run(command)
        program_path = os.path.join(self.soft_path, "data_process_sngl", "orientation_correction.exe")
        command = [
            program_path,
            "-id", self.input_dir,
            "-od", new_dir,
            "-if", os.path.join(new_dir, "orientation_estimation.bin"),
            "-iodf", self.pol_format,
            "-ofr", str(self.row_offset),
            "-ofc", str(self.col_offset),
            "-fnr", str(self.row_final),
            "-fnc", str(self.col_final),
            "-mask", self.mask_file
        ]
        subprocess.run(command)
        shutil.copy(os.path.join(self.input_dir, "config.txt"), os.path.join(new_dir, "config.txt"))
        shutil.copy(os.path.join(self.input_dir, "mask_valid_pixels.bin"), os.path.join(new_dir, "mask_valid_pixels.bin"))
        self.input_dir = new_dir
        self.output_dir = new_dir
        self.mask_file = os.path.join(new_dir, "mask_valid_pixels.bin")
        self.create_pauli_rgb_file(self.input_dir, os.path.join(self.input_dir, "PauliRGB.bmp"), 1, 0, 0, 0, 0, 0, 0)
        self.create_bmp_file(os.path.join(new_dir, "orientation_estimation.bin"), os.path.join(new_dir, "orientation_estimation.bmp"), "float", "real", "jet", 0, -90, 90, "black")

    def basis_change(self, orientation_angle, ellipticity_angle):
        if self.pol_format == "S2":
            new_dir = os.path.abspath(os.path.join(self.root_dir, os.path.pardir, os.path.basename(self.root_dir) + "_ELL"))
            self.root_dir = new_dir
        else:
            new_dir = os.path.abspath(os.path.join(self.root_dir, os.path.pardir, os.path.basename(self.root_dir) + "_ELL", self.pol_format))
            self.root_dir = os.path.abspath(os.path.join(new_dir, os.path.pardir))
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        program_path = os.path.join(self.soft_path, "basis_change", "basis_change.exe")
        command = [
            program_path,
            "-id", self.input_dir,
            "-od", new_dir,
            "-iodf", self.pol_format,    # "S2", "C3", "T3"
            "-ofr", str(self.row_offset),
            "-ofc", str(self.col_offset),
            "-fnr", str(self.row_final),
            "-fnc", str(self.col_final),
            "-phi", str(orientation_angle),
            "-tau", str(ellipticity_angle),
        ]
        subprocess.run(command)
        shutil.copy(os.path.join(self.input_dir, "config.txt"), os.path.join(new_dir, "config.txt"))
        self.input_dir = new_dir
        self.output_dir = new_dir
        self.create_mask_valid_pixels()
        self.mask_file = os.path.join(new_dir, "mask_valid_pixels.bin")
        self.create_bmp_file(self.mask_file, os.path.join(new_dir, "mask_valid_pixels.bmp"), "float", "real", "jet", 0, 0, 1, "black")


# class Tools(PolSARpro):
#     def __init__(self, soft_path, input_dir, output_dir, pol_format, row_offset, col_offset, row_final, col_final):
#         super().__init__(soft_path, input_dir, output_dir, pol_format, row_offset, col_offset, row_final, col_final)
#
#     def rawbinary_convert_RealImag_S2(self, ieee, symmetrisation, subsampling_az, subsampling_rg, file1, file2, file3, file4, file5, file6, file7, file8):
#         program_path = os.path.join(self.soft_path, "data_import", "rawbinary_convert_RealImag_S2.exe")
#         command = [
#             program_path,
#             self.output_dir,
#             str(self.col_final-self.col_offset),
#             str(self.row_offset),
#             str(self.col_offset),
#             str(self.row_final),
#             str(self.col_final),
#             str(ieee),
#             str(symmetrisation),
#             self.pol_format,
#             str(subsampling_az),
#             str(subsampling_rg),
#             file1, file2, file3, file4, file5, file6, file7, file8
#         ]
#         subprocess.run(command)
#         self.create_mask_valid_pixels()
#         self.create_bmp_file(os.path.join(self.output_dir, "mask_valid_pixels.bin"), os.path.join(self.output_dir, "mask_valid_pixels.bmp"), "float", "real", "jet", 1, 0, 1, "black")
#         self.create_pauli_rgb_file(self.output_dir, self.output_dir, 1, 0, 0, 0, 0, 0, 0)
