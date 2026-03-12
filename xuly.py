# xuly.py - Logic nghiep vu OOP, luu trong bo nho
import random, string
from datetime import datetime

DANH_SACH_MAU = ["#E57373","#F06292","#BA68C8","#7986CB","#4FC3F7",
                 "#4DB6AC","#81C784","#FFD54F","#FF8A65","#A1887F","#90A4AE","#F48FB1"]

def layMauAvatar(viTri: int) -> str:
    return DANH_SACH_MAU[viTri % len(DANH_SACH_MAU)]

def chuyenKhongDau(text: str) -> str:
    bang = str.maketrans(
        "áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ",
        "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd"
    )
    return text.lower().translate(bang)

DIA_DIEM = {
    "vung tau": ["Bai Sau","Banh khot Vung Tau","Bai Truoc","Hai Dang","Ho May Park"],
    "da lat":   ["Vuon hoa","Ga xe lua","Ho Tuyen Lam","Vuon dau tay","Thac Datanla"],
    "nha trang":["Dao Hon Mun","VinWonders","Nem nuong Ninh Hoa","Bai Tran Phu","Thap Ba Ponagar"],
    "phan thiet":["Doi cat Mui Ne","Suoi Tien","Banh canh cha ca","Luot van dieu","Bau Trang"],
}

def goiYDiaDiem(viTri: str) -> str:
    k = chuyenKhongDau(viTri)
    for key, ds in DIA_DIEM.items():
        if key in k:
            return f"Goi y tai {viTri}:\n" + "\n".join(f"{i+1}. {d}" for i,d in enumerate(ds))
    return f"Khong tim thay goi y cho '{viTri}'. Thu: Vung Tau, Da Lat, Nha Trang, Phan Thiet."


# ---- ThanhVien ----

class ThanhVien:
    def __init__(self, ten: str, viTri: int, ghiChu: str = ""):
        self.ten = ten
        self.ghiChu = ghiChu
        self.mauAvatar = layMauAvatar(viTri)
        self.soDu = 0.0       # + = duoc no, - = dang no
        self._daChi = 0.0     # giu lai de bao cao tong chi

    def layKyTuDau(self) -> str:
        return self.ten[0].upper() if self.ten else "?"

    def laySoDu(self) -> float:
        return self.soDu

    # Khi chi: nguoi chi duoc no them, nguoi duoc chi no them
    def themDaChi(self, x):    self.soDu += x; self._daChi += x
    def themDuocChi(self, x):  self.soDu -= x
    # Khi thanh toan: nguoi tra giam no, nguoi nhan giam duoc no
    def themDaTra(self, x):    self.soDu += x   # tra tien = giam no (am -> it am hon)
    def themDuocNhan(self, x): self.soDu -= x   # nhan tien = giam duoc no (duong -> it duong hon)
    # Alias
    def themKhoanDaChi(self, x):   self.themDaChi(x)
    def themKhoanDuocChi(self, x): self.themDuocChi(x)
    def themKhoanDaTra(self, x):   self.themDaTra(x)
    def themKhoanDuocNhan(self, x):self.themDuocNhan(x)


# ---- GiaoDich ----

class GiaoDichChi:
    LOAI_CHI = "chi"
    def __init__(self, soTien, noiDung, nguoiChi, danhSachNguoiNhan, ghiChu=""):
        self.soTien = soTien
        self.noiDung = noiDung
        self.nguoiChi = nguoiChi
        self.danhSachNguoiNhan = danhSachNguoiNhan
        self.ghiChu = ghiChu
        self.thoiGian = datetime.now()
        self.loai = self.LOAI_CHI
        self.danhSachAnh: list = []

    def layPhanChiaMotNguoi(self) -> float:
        n = len(self.danhSachNguoiNhan)
        return self.soTien / n if n > 0 else 0.0

    def layMoTaLichSu(self) -> str:
        ds = ", ".join(self.danhSachNguoiNhan)
        tg = self.thoiGian.strftime("%H:%M %d/%m/%Y")
        return f"Chi: {self.nguoiChi} chi {self.soTien:,.0f}d cho {ds} | {self.noiDung} | {tg}"


class GiaoDichThanhToan:
    LOAI_THANH_TOAN = "thanhtoan"
    LOAI_TUY_CHON   = "tuychon"
    LOAI_LAN_LUOT   = "lanluot"
    def __init__(self, nguoiTra, nguoiNhan, soTien, loai=None):
        self.nguoiTra = nguoiTra
        self.nguoiNhan = nguoiNhan
        self.soTien = soTien
        self.loai = loai or self.LOAI_TUY_CHON
        self.thoiGian = datetime.now()

    def layMoTaLichSu(self) -> str:
        tg = self.thoiGian.strftime("%H:%M %d/%m/%Y")
        return f"Tra: {self.nguoiTra} tra {self.nguoiNhan} {self.soTien:,.0f}d | {tg}"


# ---- Nhom ----

class Nhom:
    def __init__(self, tenNhom: str, viTri: str, nguoiTao: str):
        self.tenNhom = tenNhom
        self.viTri = viTri
        self.nguoiTao = nguoiTao
        self.ngayTao = datetime.now()
        self.maNhom = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.danhSachThanhVien: list[ThanhVien] = []
        self.danhSachGiaoDich: list = []

    def themThanhVien(self, ten: str, ghiChu: str = "") -> ThanhVien:
        tv = ThanhVien(ten, len(self.danhSachThanhVien), ghiChu)
        self.danhSachThanhVien.append(tv)
        return tv

    def layThanhVienTheoTen(self, ten: str):
        return next((tv for tv in self.danhSachThanhVien if tv.ten == ten), None)

    def layTongChi(self) -> float:
        return sum(gd.soTien for gd in self.danhSachGiaoDich if isinstance(gd, GiaoDichChi))

    def themGiaoDichChi(self, gd: GiaoDichChi):
        self.danhSachGiaoDich.append(gd)
        tv = self.layThanhVienTheoTen(gd.nguoiChi)
        if tv: tv.themDaChi(gd.soTien)
        phan = gd.layPhanChiaMotNguoi()
        for ten in gd.danhSachNguoiNhan:
            tv = self.layThanhVienTheoTen(ten)
            if tv: tv.themDuocChi(phan)

    def themGiaoDichThanhToan(self, gd: GiaoDichThanhToan):
        self.danhSachGiaoDich.append(gd)
        tra = self.layThanhVienTheoTen(gd.nguoiTra)
        nhan = self.layThanhVienTheoTen(gd.nguoiNhan)
        if tra:  tra.themDaTra(gd.soTien)
        if nhan: nhan.themDuocNhan(gd.soTien)

    def tinhNoGiaNoGiuaThanhVien(self) -> list[dict]:
        """Tinh ai no ai bao nhieu (thuat toan toi uu so giao dich)"""
        soDu = {tv.ten: tv.laySoDu() for tv in self.danhSachThanhVien}
        duong = [(t, v)  for t, v in soDu.items() if v >  0.01]
        am    = [(t, -v) for t, v in soDu.items() if v < -0.01]
        ketQua, i, j = [], 0, 0
        while i < len(am) and j < len(duong):
            soTra = min(am[i][1], duong[j][1])
            ketQua.append({"nguoiNo": am[i][0], "nguoiDuocNo": duong[j][0], "soTien": soTra})
            am[i]    = (am[i][0],    am[i][1]    - soTra)
            duong[j] = (duong[j][0], duong[j][1] - soTra)
            if am[i][1] < 0.01:    i += 1
            if duong[j][1] < 0.01: j += 1
        return ketQua

    def layTongNoGiuaHaiNguoi(self, nguoiTra: str, nguoiNhan: str) -> float:
        return sum(d["soTien"] for d in self.tinhNoGiaNoGiuaThanhVien()
                   if d["nguoiNo"] == nguoiTra and d["nguoiDuocNo"] == nguoiNhan)

    def layNguoiNoNhieuNhat(self) -> str:
        no = {tv.ten: -tv.laySoDu() for tv in self.danhSachThanhVien if tv.laySoDu() < -0.01}
        if not no: return "Khong co ai dang no."
        ten = max(no, key=no.get)
        ct = "\n".join(f"  - {d['nguoiDuocNo']}: {d['soTien']:,.0f}d"
                        for d in self.tinhNoGiaNoGiuaThanhVien() if d["nguoiNo"] == ten)
        return f"{ten} dang no nhieu nhat: {no[ten]:,.0f}d\n{ct}"


# ---- QuanLyUngDung ----

class QuanLyUngDung:
    def __init__(self):
        self.nhomHienTai: Nhom | None = None
        self._soTienChi = 0.0
        self._noiDungChi = self._ghiChuChi = self._nguoiChi = ""
        self._danhSachNguoiNhan: list = []
        self._danhSachAnhChi: list = []
        self._nguoiTra = self._nguoiNhan = ""
        self._loaiThanhToan = GiaoDichThanhToan.LOAI_TUY_CHON

    # -- Nhom --

    def taoNhomMoi(self, tenNhom, viTri, nguoiTao) -> bool:
        if not tenNhom: return False
        self.nhomHienTai = Nhom(tenNhom, viTri, nguoiTao)
        self.nhomHienTai.themThanhVien(nguoiTao, "Truong nhom")
        return True

    def themThanhVienVaoNhom(self, ten: str) -> bool:
        if not self.nhomHienTai or not ten: return False
        self.nhomHienTai.themThanhVien(ten)
        return True

    def themThanhVienMoiTuTinhNang(self, ten: str, ghiChu: str = "") -> bool:
        if not self.nhomHienTai or not ten: return False
        self.nhomHienTai.themThanhVien(ten, ghiChu)
        return True

    def layTenNhom(self) -> str:
        return self.nhomHienTai.tenNhom if self.nhomHienTai else ""

    def layTongChi(self) -> str:
        return f"{self.nhomHienTai.layTongChi():,.0f}d" if self.nhomHienTai else "0d"

    def layDanhSachThanhVien(self) -> list:
        return self.nhomHienTai.danhSachThanhVien if self.nhomHienTai else []

    def layDashboardThanhVien(self) -> list[dict]:
        ketQua = []
        for tv in self.layDanhSachThanhVien():
            sd = tv.laySoDu()
            mau = "#2E7D32" if sd > 0.01 else "#C62828" if sd < -0.01 else "#9E9E9E"
            sDuStr = (f"+{sd:,.0f}d" if sd > 0.01
                      else f"{sd:,.0f}d" if sd < -0.01 else "0d")
            ketQua.append({"ten": tv.ten, "kyTuDau": tv.layKyTuDau(),
                           "mauAvatar": tv.mauAvatar, "soDu": sDuStr, "mauSoDu": mau})
        return ketQua

    def layThongTinNhom(self) -> dict | None:
        if not self.nhomHienTai: return None
        n = self.nhomHienTai
        return {"tenNhom": n.tenNhom, "viTri": n.viTri, "nguoiTao": n.nguoiTao,
                "ngayTao": n.ngayTao.strftime("%d/%m/%Y"), "maNhom": n.maNhom,
                "soThanhVien": len(n.danhSachThanhVien)}

    def capNhatThongTinNhom(self, tenMoi, viTriMoi) -> bool:
        if not self.nhomHienTai: return False
        self.nhomHienTai.tenNhom = tenMoi
        self.nhomHienTai.viTri = viTriMoi
        return True

    def nhanBanNhom(self, tenMoi: str, danhSachTen: list) -> bool:
        if not self.nhomHienTai or not tenMoi: return False
        nhomMoi = Nhom(tenMoi, self.nhomHienTai.viTri, self.nhomHienTai.nguoiTao)
        for ten in danhSachTen:
            tv = self.nhomHienTai.layThanhVienTheoTen(ten)
            if tv: nhomMoi.themThanhVien(tv.ten, tv.ghiChu)
        self.nhomHienTai = nhomMoi
        return True

    def xoaNhom(self):
        self.__init__()

    # -- Khoan chi --

    def datSoTienChi(self, x): self._soTienChi = x
    def datNoiDungChi(self, x): self._noiDungChi = x
    def datGhiChuChi(self, x): self._ghiChuChi = x
    def datNguoiChi(self, x): self._nguoiChi = x
    def layNguoiChi(self): return self._nguoiChi
    def datDanhSachNguoiNhan(self, x): self._danhSachNguoiNhan = x
    def layDanhSachNguoiNhan(self): return self._danhSachNguoiNhan
    def themAnhChi(self, x): self._danhSachAnhChi.append(x)

    def layDanhSachAnhChi(self) -> list:
        """Lay tat ca anh tu cac giao dich da luu + anh chua luu hien tai"""
        ketQua = []
        if self.nhomHienTai:
            for gd in self.nhomHienTai.danhSachGiaoDich:
                if isinstance(gd, GiaoDichChi):
                    ketQua.extend(gd.danhSachAnh)
        ketQua.extend(self._danhSachAnhChi)
        return ketQua

    def xacNhanKhoanChi(self) -> bool:
        if not self.nhomHienTai or not self._nguoiChi or not self._danhSachNguoiNhan or self._soTienChi <= 0:
            return False
        gd = GiaoDichChi(self._soTienChi, self._noiDungChi, self._nguoiChi,
                         self._danhSachNguoiNhan, self._ghiChuChi)
        gd.danhSachAnh = list(self._danhSachAnhChi)
        self.nhomHienTai.themGiaoDichChi(gd)
        self._soTienChi = 0.0
        self._noiDungChi = self._ghiChuChi = self._nguoiChi = ""
        self._danhSachNguoiNhan = self._danhSachAnhChi = []
        return True

    # -- Thanh toan --

    def datNguoiTra(self, x): self._nguoiTra = x
    def layNguoiTra(self): return self._nguoiTra
    def datNguoiNhan(self, x): self._nguoiNhan = x
    def layNguoiNhan(self): return self._nguoiNhan
    def datLoaiThanhToan(self, x): self._loaiThanhToan = x

    def layTongNoHienCo(self) -> float:
        if not self.nhomHienTai or not self._nguoiTra or not self._nguoiNhan: return 0.0
        return self.nhomHienTai.layTongNoGiuaHaiNguoi(self._nguoiTra, self._nguoiNhan)

    def xacNhanThanhToan(self) -> bool:
        if not self.nhomHienTai or not self._nguoiTra or not self._nguoiNhan: return False
        soTien = self.nhomHienTai.layTongNoGiuaHaiNguoi(self._nguoiTra, self._nguoiNhan)
        if soTien <= 0: return False  # khong co no giua 2 nguoi nay
        gd = GiaoDichThanhToan(self._nguoiTra, self._nguoiNhan, soTien, self._loaiThanhToan)
        self.nhomHienTai.themGiaoDichThanhToan(gd)
        self._nguoiTra = self._nguoiNhan = ""
        self._loaiThanhToan = GiaoDichThanhToan.LOAI_TUY_CHON
        return True

    # -- Truy xuat --

    def layLichSuHoatDong(self) -> list[str]:
        if not self.nhomHienTai: return []
        return [gd.layMoTaLichSu() for gd in reversed(self.nhomHienTai.danhSachGiaoDich)]

    def layGoiYChiaTien(self) -> list[dict]:
        return self.nhomHienTai.tinhNoGiaNoGiuaThanhVien() if self.nhomHienTai else []

    def layTongKetChiTieu(self) -> str:
        if not self.nhomHienTai: return "Chua co du lieu."
        n = self.nhomHienTai
        lines = [f"Tong ket nhom: {n.tenNhom}", f"Tong chi: {n.layTongChi():,.0f}d", ""]
        for i, gd in enumerate(n.danhSachGiaoDich, 1):
            if isinstance(gd, GiaoDichChi):
                lines.append(f"{i}. {gd.nguoiChi} -> {', '.join(gd.danhSachNguoiNhan)}: {gd.soTien:,.0f}d ({gd.noiDung})")
            elif isinstance(gd, GiaoDichThanhToan):
                lines.append(f"{i}. {gd.nguoiTra} tra {gd.nguoiNhan}: {gd.soTien:,.0f}d")
        lines.append("\nSo du:")
        for tv in n.danhSachThanhVien:
            sd = tv.laySoDu()
            trang = f"+{sd:,.0f}d (duoc no)" if sd > 0.01 else f"{sd:,.0f}d (dang no)" if sd < -0.01 else "0d (can bang)"
            lines.append(f"  {tv.ten}: {trang}")
        return "\n".join(lines)

    def layThongTinNoNhieuNhat(self) -> str:
        return self.nhomHienTai.layNguoiNoNhieuNhat() if self.nhomHienTai else "Chua co du lieu."

    def layGoiYDiaDiem(self) -> str:
        return goiYDiaDiem(self.nhomHienTai.viTri) if self.nhomHienTai else "Chua nhap vi tri."

    def layDuLieuBaoCao(self) -> dict:
        if not self.nhomHienTai: return {}
        n = self.nhomHienTai
        gdList = [{"soTien": gd.soTien, "noiDung": gd.noiDung, "nguoiChi": gd.nguoiChi,
                   "nguoiNhan": ", ".join(gd.danhSachNguoiNhan),
                   "thoiGian": gd.thoiGian.strftime("%d/%m/%Y %H:%M"), "ghiChu": gd.ghiChu}
                  for gd in n.danhSachGiaoDich if isinstance(gd, GiaoDichChi)]
        return {"tenNhom": n.tenNhom, "ngayTao": n.ngayTao.strftime("%d/%m/%Y"),
                "tongChi": n.layTongChi(),
                "danhSachGiaoDich": gdList,
                "tongChiThanhVien": {tv.ten: tv._daChi for tv in n.danhSachThanhVien},
                "goiYChiaTien": n.tinhNoGiaNoGiuaThanhVien()}

    def layDanhSachThongBao(self) -> list[dict]:
        if not self.nhomHienTai: return []
        ketQua = []
        for gd in reversed(self.nhomHienTai.danhSachGiaoDich[-5:]):
            tg = gd.thoiGian.strftime("%H:%M %d/%m/%Y")
            if isinstance(gd, GiaoDichChi):
                ketQua.append({"tieuDe": "Khoan chi moi",
                               "noiDung": f"{gd.nguoiChi} chi {gd.soTien:,.0f}d cho {gd.noiDung}",
                               "thoiGian": tg, "daDoc": False})
            elif isinstance(gd, GiaoDichThanhToan):
                ketQua.append({"tieuDe": "Thanh toan",
                               "noiDung": f"{gd.nguoiTra} tra {gd.nguoiNhan} {gd.soTien:,.0f}d",
                               "thoiGian": tg, "daDoc": True})
        return ketQua
