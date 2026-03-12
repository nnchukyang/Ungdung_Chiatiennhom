import sys, os
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QListWidget, QListWidgetItem,
    QWidget, QHBoxLayout, QLabel, QCheckBox, QMessageBox, QFileDialog
)
from PyQt6.QtGui import QFont, QPixmap, QPainter
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtPrintSupport import QPrinter
from xuly import QuanLyUngDung, GiaoDichThanhToan



def taoAvatar(kyTu: str, mau: str, size: int = 32) -> QLabel:
    lbl = QLabel(kyTu)
    lbl.setFixedSize(size, size)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    r = size // 2
    lbl.setStyleSheet(f"background:{mau};color:white;border-radius:{r}px;"
                      f"font-weight:bold;font-size:{size//3+2}px;")
    return lbl

def taoQRPixmap(van_ban: str, kich_thuoc: int = 120) -> "QPixmap":
    from PyQt6.QtGui import QPixmap, QPainter, QColor
    from PyQt6.QtCore import Qt

    data = van_ban.encode("utf-8")
    bits = "0100"
    bits += format(len(data), "08b")
    for b in data:
        bits += format(b, "08b")
    bits += "0000"
    while len(bits) % 8: bits += "0"
    padding = ["11101100", "00010001"]
    i = 0
    while len(bits) < 128:
        bits += padding[i % 2]; i += 1

    N = 21
    mat = [[0]*N for _ in range(N)]

    def dat(r, c, v): mat[r][c] = v

    def finder(r0, c0):
        for dr in range(7):
            for dc in range(7):
                v = 1 if (dr in (0,6) or dc in (0,6) or (1<dr<5 and 1<dc<5)) else 0
                dat(r0+dr, c0+dc, v)
    finder(0,0); finder(0,14); finder(14,0)

    for i in range(8):
        for r,c in [(7,i),(i,7),(7,14+i-7 if i<7 else 7),(i,13),(14+i-7 if i<7 else 14,7),(7,i)]:
            pass

    for i in range(8, 13):
        mat[6][i] = 1 if i%2==0 else 0
        mat[i][6] = 1 if i%2==0 else 0

    fmt = "101010000010010"
    fmt_pos = [(8,0),(8,1),(8,2),(8,3),(8,4),(8,5),(8,7),(8,8),
               (7,8),(5,8),(4,8),(3,8),(2,8),(1,8),(0,8)]
    for idx, (r,c) in enumerate(fmt_pos):
        mat[r][c] = int(fmt[idx])
    for i in range(7):
        mat[8][N-1-i] = int(fmt[i])
    for i in range(7,15):
        mat[N-15+i][8] = int(fmt[i])
    mat[N-8][8] = 1

    data_bits = bits
    bi = 0
    col = N-1
    going_up = True
    while col > 0:
        if col == 6: col -= 1
        rows = range(N-1,-1,-1) if going_up else range(N)
        for row in rows:
            for dc in range(2):
                c = col - dc
                if mat[row][c] != 0: continue
                if bi < len(data_bits):
                    bit = int(data_bits[bi]); bi += 1
                else:
                    bit = 0
                if (row + c) % 2 == 0: bit ^= 1
                mat[row][c] = bit + 2
        col -= 2
        going_up = not going_up

    def la_den(r, c):
        v = mat[r][c]
        if v == 1: return True
        if v == 3: return True
        return False

    px = QPixmap(kich_thuoc, kich_thuoc)
    px.fill(QColor("white"))
    p = QPainter(px)
    cell = kich_thuoc / N
    for r in range(N):
        for c in range(N):
            if la_den(r, c):
                p.fillRect(int(c*cell), int(r*cell),
                           max(1,int(cell)), max(1,int(cell)),
                           QColor("black"))
    p.end()
    return px


class WidgetThanhVienDashboard(QWidget):
    def __init__(self, ten, kyTuDau, mauAvatar, soDu, mauSoDu, parent=None):
        super().__init__(parent)
        lo = QHBoxLayout(self)
        lo.setContentsMargins(4, 4, 4, 4); lo.setSpacing(8)
        lblSoDu = QLabel(soDu)
        lblSoDu.setStyleSheet(f"font-size:12px;color:{mauSoDu};font-weight:bold;background:transparent;")
        lblSoDu.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lo.addWidget(taoAvatar(kyTuDau, mauAvatar, 36))
        lo.addWidget(QLabel(ten), 1)
        lo.addWidget(lblSoDu)
        self.setStyleSheet("background:transparent;")

class WidgetChonMot(QWidget):
    MAU_THUONG = "#FFF8E1"
    MAU_CHON   = "#FFCC80"

    def __init__(self, ten, kyTuDau, mauAvatar, parent=None):
        super().__init__(parent)
        lo = QHBoxLayout(self)
        lo.setContentsMargins(8, 6, 8, 6); lo.setSpacing(8)
        self._ten = ten
        self._chon = False
        self._tick = QLabel("\u2713")
        self._tick.setStyleSheet("font-size:16px;color:#FF6F00;font-weight:bold;background:transparent;")
        self._tick.setVisible(False)
        lo.addWidget(taoAvatar(kyTuDau, mauAvatar))
        lo.addWidget(QLabel(ten), 1)
        lo.addWidget(self._tick)
        self._capNhatNen()

    def _capNhatNen(self):
        mau = self.MAU_CHON if self._chon else self.MAU_THUONG
        self.setStyleSheet(f"QWidget{{background:{mau};border-radius:10px;margin:2px;}}")
        self._tick.setVisible(self._chon)

    def datChon(self, val: bool):
        self._chon = val; self._capNhatNen()

    def layTen(self): return self._ten
    def laDuocChon(self): return self._chon

class WidgetChonNhieu(QWidget):
    def __init__(self, ten, kyTuDau, mauAvatar, parent=None):
        super().__init__(parent)
        lo = QHBoxLayout(self)
        lo.setContentsMargins(4, 4, 4, 4); lo.setSpacing(8)
        self._ten = ten
        self.cb = QCheckBox()
        self.cb.setStyleSheet("background:transparent;")
        lo.addWidget(self.cb)
        lo.addWidget(taoAvatar(kyTuDau, mauAvatar))
        lo.addWidget(QLabel(ten), 1)
        self.setStyleSheet("QWidget{background:#FFF3E0;border-radius:10px;margin:2px;}")

    def layTen(self): return self._ten
    def laDuocChon(self): return self.cb.isChecked()

def layTenDuocChon(listWidget, loai):
    for i in range(listWidget.count()):
        w = listWidget.itemWidget(listWidget.item(i))
        if isinstance(w, loai) and w.laDuocChon():
            return w.layTen()
    return None

def layDanhSachTenDuocChon(listWidget, loai):
    ws = [listWidget.itemWidget(listWidget.item(i)) for i in range(listWidget.count())]
    return [w.layTen() for w in ws if isinstance(w, loai) and w.laDuocChon()]

def dienList(listWidget, danhSachTV, loai, cao=50):
    listWidget.clear()
    for tv in danhSachTV:
        item = QListWidgetItem()
        w = loai(tv.ten, tv.layKyTuDau(), tv.mauAvatar)
        item.setSizeHint(QSize(listWidget.width() or 260, cao))
        listWidget.addItem(item)
        listWidget.setItemWidget(item, w)

class CuaSoChinh(QMainWindow):
    I_SPLASH, I_KHOI_TAO, I_DS_TV, I_TRANG_CHU  = 0, 1, 2, 3
    I_TINH_NANG, I_THEM_TV, I_CHI, I_CHON_CHI   = 4, 5, 6, 7
    I_CHON_CHO_AI, I_TT, I_CHON_TRA, I_CHON_NHAN = 8, 9, 10, 11
    I_LS, I_TBAO, I_TTIN, I_AI, I_AI_TL           = 12, 13, 14, 15, 16
    I_GOI_Y, I_TUY_CHON, I_CHINH_SUA, I_NHAN_BAN  = 17, 18, 19, 20

    def __init__(self):
        super().__init__()
        uic.loadUi("giaodienapp.ui", self)
        self.ql = QuanLyUngDung()
        self._apDungStyle()
        self._ketNoiSuKien()
        self.AppChiaTien.setCurrentIndex(self.I_SPLASH)
        QTimer.singleShot(2000, lambda: self.chuyenTrang(self.I_KHOI_TAO))

    def _apDungStyle(self):
        self.setStyleSheet("""
            /* === NEN TONG === */
            QMainWindow, QWidget {
                background-color: #FFF8E1;
                font-family: Arial;
                font-size: 13px;
                font-weight: bold;
                color: #E65100;
            }

            /* === LABEL === */
            QLabel {
                color: #BF360C;
                font-weight: bold;
                font-size: 13px;
                background: transparent;
            }

            /* === O NHAP LIEU === */
            QLineEdit {
                background-color: #FFFFFF;
                color: #E65100;
                font-weight: bold;
                border: 2px solid #FFCC80;
                border-radius: 8px;
                padding: 4px 10px;
            }
            QLineEdit:focus {
                border: 2px solid #FF6F00;
                background-color: #FFF3E0;
            }
            QLineEdit:disabled {
                background-color: #F5F5F5;
                color: #BDBDBD;
                border: 2px solid #E0E0E0;
            }

            /* === NUT BUTTON === */
            QPushButton {
                background-color: #FF6F00;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 13px;
                border-radius: 10px;
                padding: 6px 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #E65100;
            }
            QPushButton:pressed {
                background-color: #BF360C;
            }
            QPushButton:disabled {
                background-color: #FFCC80;
                color: #FFFFFF;
            }

            /* === LIST WIDGET === */
            QListWidget {
                background-color: #FFFFFF;
                border: 2px solid #FFCC80;
                border-radius: 10px;
                outline: none;
            }
            QListWidget::item {
                padding: 2px;
            }
            QListWidget::item:selected {
                background-color: #FFF3E0;
                border-radius: 8px;
            }

            /* === SCROLL BAR === */
            QScrollBar:vertical {
                background: #FFF8E1;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #FFCC80;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical { height: 0px; }

            /* === TEN NHOM (hien tren nen dam) === */
            QLabel#lblTenNhomTrangChu, QLabel#lblTenNhomTinhNang,
            QLabel#lblTenNhomHoatDong, QLabel#lblTenNhomAI,
            QLabel#lblTenNhomAITraLoi, QLabel#lblTenNhomTuyChon,
            QLabel#lblTenNhomNhanBan {
                color: #FFF8E1;
                font-size: 15px;
                font-weight: bold;
                background: transparent;
            }

            /* Trang nen sang -> dung mau dam */
            QLabel#lblTenNhomThongBao, QLabel#lblTenNhomThongTin,
            QLabel#lblTenNhomTTin {
                color: #BF360C;
                font-size: 15px;
                font-weight: bold;
                background: transparent;
            }
        """)

    def chuyenTrang(self, idx: int):
        self.AppChiaTien.setCurrentIndex(idx)

    def chuyenSangTrangChu(self):
        self._dienDashboard(self.listTrangChu)
        self.lblTenNhomTrangChu.setText(self.ql.layTenNhom())
        self.lblTongChi.setText(f"Tong: {self.ql.layTongChi()}")
        self.chuyenTrang(self.I_TRANG_CHU)

    def chuyenSangTinhNang(self):
        self._dienDashboard(self.listTinhNang)
        self.lblTenNhomTinhNang.setText(self.ql.layTenNhom())
        self.lblTongChiTinhNang.setText(f"Tong: {self.ql.layTongChi()}")
        self.chuyenTrang(self.I_TINH_NANG)

    def _dienDashboard(self, listWidget):
        listWidget.clear()
        for info in self.ql.layDashboardThanhVien():
            item = QListWidgetItem()
            w = WidgetThanhVienDashboard(info["ten"], info["kyTuDau"],
                info["mauAvatar"], info["soDu"], info["mauSoDu"])
            item.setSizeHint(QSize(260, 50))
            listWidget.addItem(item)
            listWidget.setItemWidget(item, w)

    def _ketNoiSuKien(self):
        # Index 1
        self.btnHuyKhoiTao.clicked.connect(self.close)
        self.btnTiepTucKhoiTao.clicked.connect(self.xuLyTiepTucKhoiTao)
        # Index 2
        self.btnHuyThanhVien.clicked.connect(lambda: self.chuyenTrang(self.I_KHOI_TAO))
        self.btnThemTen.clicked.connect(self.xuLyThemTenBuoc2)
        self.btnTiepTucThanhVien.clicked.connect(self.xuLyTiepTucThanhVien)
        # Index 3
        self.btnAI.clicked.connect(self._moAI)
        self.btnAnh.clicked.connect(self.xuLyXuatAnhPDF)
        self.btnBaoCao.clicked.connect(self.xuLyXuatBaoCao)
        self.btnGoiYChia.clicked.connect(self._moGoiYChiaTien)
        self.btnLichSu.clicked.connect(self._moLichSu)
        self.btnNhacNo.clicked.connect(self.xuLyNhacNo)
        self.btnTBao.clicked.connect(self._moThongBao)
        self.btnTTin.clicked.connect(self._moThongTin)
        self.btnTinhNang.clicked.connect(self.chuyenSangTinhNang)
        self.btnTuyChinh.clicked.connect(self._moTuyChon)
        # Index 4
        self.btnChi.clicked.connect(self._moKhoanChi)
        self.btnTToan.clicked.connect(self._moThanhToan)
        self.btnTat.clicked.connect(self.chuyenSangTrangChu)
        self.btnThanhVien.clicked.connect(lambda: self.chuyenTrang(self.I_THEM_TV))
        # Index 5
        self.btnTroVe.clicked.connect(self.chuyenSangTinhNang)
        self.btnThemTVMoi.clicked.connect(self.xuLyThemTVMoi)
        # Index 6
        self.btnHuyChi.clicked.connect(self.chuyenSangTinhNang)
        self.btnXongChi.clicked.connect(self.xuLyXongChi)
        self.btnNguoiChi.clicked.connect(
            lambda: self._moChonMot(self.listChonNguoiChi, self.I_CHON_CHI))
        self.btnNguoiDuocChi.clicked.connect(
            lambda: self._moChonNhieu(self.listNguoiDuocChi, self.I_CHON_CHO_AI))
        self.btnAnhChi.clicked.connect(self.xuLyThemAnhChi)
        self.btnThoiGianChi.clicked.connect(lambda: None)
        # Index 7
        self.btnXongNguoiChi.clicked.connect(self.xuLyXongChonNguoiChi)
        self.btnXongChonNguoiChi.clicked.connect(self.xuLyXongChonNguoiChi)
        # Index 8
        self.btnXongNguoiDuocChi.clicked.connect(self.xuLyXongChonNguoiDuocChi)
        self.btnXongChonNguoiDuocChi.clicked.connect(self.xuLyXongChonNguoiDuocChi)
        # Index 9
        self.btnHuyTToan.clicked.connect(self.chuyenSangTinhNang)
        self.btnXongThanhToan.clicked.connect(self.xuLyXongThanhToan)
        self.btnNguoiTra.clicked.connect(
            lambda: self._moChonMot(self.listNguoiTra, self.I_CHON_TRA))
        self.btnNguoiNhan.clicked.connect(
            lambda: self._moChonMot(self.listNguoiNhan, self.I_CHON_NHAN))
        self.btnTToanTuyChon.clicked.connect(
            lambda: self.ql.datLoaiThanhToan(GiaoDichThanhToan.LOAI_TUY_CHON))
        self.btnTToanLanLuot.clicked.connect(
            lambda: self.ql.datLoaiThanhToan(GiaoDichThanhToan.LOAI_LAN_LUOT))
        # Index 10, 11
        self.btnXongNguoiTra.clicked.connect(self.xuLyXongChonNguoiTra)
        self.btnXongChonNguoiTra.clicked.connect(self.xuLyXongChonNguoiTra)
        self.btnXongNguoiNhan.clicked.connect(self.xuLyXongChonNguoiNhan)
        self.btnXongChonNguoiNhan.clicked.connect(self.xuLyXongChonNguoiNhan)
        # Index 12, 13, 14
        self.btnThongBaoLichSu.clicked.connect(self._moThongBao)
        self.btnThongTinThongBao.clicked.connect(self._moThongTin)
        self.btnTrangChu.clicked.connect(self.chuyenSangTrangChu)
        # Index 15
        self.btnTatAI.clicked.connect(self.chuyenSangTrangChu)
        self.btnTongKetChiTieu.clicked.connect(lambda: self._xuLyAI("tong ket"))
        self.btnNoNhieuNhat.clicked.connect(lambda: self._xuLyAI("no nhieu"))
        self.btnNganSach.clicked.connect(lambda: self._xuLyAI("ngan sach"))
        self.btnChiaToiUu.clicked.connect(lambda: self._xuLyAI("toi uu"))
        self.btnDiaDiemTiepTheo.clicked.connect(lambda: self._xuLyAI("dia diem"))
        self.btnGuiAI.clicked.connect(self.xuLyGuiAI)
        self.btnMicro.clicked.connect(lambda: None)
        # Index 16
        self.btnXongAI.clicked.connect(self.chuyenSangTrangChu)
        # Index 17
        self.btnTatGoiY.clicked.connect(self.chuyenSangTrangChu)
        # Index 18
        self.btnTatTuyChon.clicked.connect(self.chuyenSangTrangChu)
        self.btnSuaNhom.clicked.connect(self._moChinhSua)
        self.btnLuuTru.clicked.connect(lambda: None)
        self.btnNhanBan.clicked.connect(self._moNhanBan)
        self.btnXoa.clicked.connect(self.xuLyXoaNhom)
        # Index 19
        self.btnThoatChinhSua.clicked.connect(self._moTuyChon)
        self.btnLuu.clicked.connect(self.xuLyLuuChinhSua)
        # Index 20
        self.btnTatCa.clicked.connect(self.xuLyChonTatCaNhanBan)
        self.btnXongNhanBan.clicked.connect(self.xuLyXongNhanBan)

    def xuLyTiepTucKhoiTao(self):
        ten = self.txtNhapTenNhom.text().strip()
        if not ten or ten == "Nhap...":
            QMessageBox.warning(self, "Loi", "Vui long nhap ten nhom!"); return
        self._tenNhomTam = ten
        self._viTriTam = self.txtNhapViTri.text().strip().replace("Nhap...", "")
        self._dsTenBuoc2 = []
        while self.listThanhVien.count() > 1:
            self.listThanhVien.takeItem(1)
        self.chuyenTrang(self.I_DS_TV)

    def xuLyThemTenBuoc2(self):
        ten = self.txtNhapTenThanhVien.text().strip()
        if not ten or ten == "Nhap...":
            QMessageBox.warning(self, "Loi", "Vui long nhap ten!"); return
        from xuly import layMauAvatar
        self._dsTenBuoc2.append(ten)
        item = QListWidgetItem()
        w = WidgetThanhVienDashboard(ten, ten[0].upper(),
            layMauAvatar(len(self._dsTenBuoc2)), "", "#333")
        item.setSizeHint(QSize(260, 44))
        self.listThanhVien.addItem(item)
        self.listThanhVien.setItemWidget(item, w)
        self.txtNhapTenThanhVien.clear()

    def xuLyTiepTucThanhVien(self):
        tenBan = self.txtNhapTenCuaBan.text().strip()
        if not tenBan or tenBan == "Nhap...":
            QMessageBox.warning(self, "Loi", "Vui long nhap ten cua ban!"); return
        self.ql.taoNhomMoi(self._tenNhomTam, self._viTriTam, tenBan)
        for ten in self._dsTenBuoc2:
            self.ql.themThanhVienVaoNhom(ten)
        self.chuyenSangTrangChu()

    def xuLyThemTVMoi(self):
        ten = self.txtThanhVienMoi.text().strip()
        if not ten or ten == "Nhap...":
            QMessageBox.warning(self, "Loi", "Vui long nhap ten!"); return
        ghiChu = self.txtGhiChuMoi.text().strip().replace("Nhap...", "")
        self.ql.themThanhVienMoiTuTinhNang(ten, ghiChu)
        QMessageBox.information(self, "Thanh cong", f"Da them {ten}!")
        self.chuyenSangTinhNang()

    def _moKhoanChi(self):
        self.txtTienChi.setText("...d")
        self.txtNoiDung.setText("Nhap...")
        self.txtGhiChuChi.setText("Nhap...")
        self.btnNguoiChi.setText("Chon nguoi chi")
        self.btnNguoiDuocChi.setText("Chon nguoi duoc chi")
        self.chuyenTrang(self.I_CHI)

    def xuLyThemAnhChi(self):
        duong, _ = QFileDialog.getOpenFileName(self, "Chon anh", "",
                                               "Hinh anh (*.png *.jpg *.jpeg)")
        if duong:
            self.ql.themAnhChi(duong)
            QMessageBox.information(self, "OK", f"Da them: {os.path.basename(duong)}")

    def xuLyXongChi(self):
        soTienStr = self.txtTienChi.text().replace(",","").replace("d","").replace(".","").strip()
        noiDung   = self.txtNoiDung.text().strip()
        if not noiDung or noiDung == "Nhap...":
            QMessageBox.warning(self, "Loi", "Vui long nhap noi dung!"); return
        try:
            soTien = float(soTienStr)
        except ValueError:
            soTien = 0.0
        if soTien <= 0:
            QMessageBox.warning(self, "Loi", "Vui long nhap so tien!"); return
        self.ql.datSoTienChi(soTien)
        self.ql.datNoiDungChi(noiDung)
        self.ql.datGhiChuChi(self.txtGhiChuChi.text().replace("Nhap...","").strip())
        if self.ql.xacNhanKhoanChi():
            self.chuyenSangTinhNang()
        else:
            QMessageBox.warning(self, "Loi", "Vui long chon nguoi chi va nguoi duoc chi!")

    def _moChonMot(self, listWidget, indexTrang):
        dienList(listWidget, self.ql.layDanhSachThanhVien(), WidgetChonMot)
        try: listWidget.itemClicked.disconnect()
        except Exception: pass
        listWidget.itemClicked.connect(lambda clicked: [
            w.datChon(listWidget.item(i) is clicked)
            for i in range(listWidget.count())
            if isinstance(w := listWidget.itemWidget(listWidget.item(i)), WidgetChonMot)
        ])
        self.chuyenTrang(indexTrang)

    def _moChonNhieu(self, listWidget, indexTrang):
        dienList(listWidget, self.ql.layDanhSachThanhVien(), WidgetChonNhieu)
        try: listWidget.itemClicked.disconnect()
        except Exception: pass
        def toggleChon(item):
            w = listWidget.itemWidget(item)
            if isinstance(w, WidgetChonNhieu):
                w.cb.setChecked(not w.cb.isChecked())
        listWidget.itemClicked.connect(toggleChon)
        self.chuyenTrang(indexTrang)

    def xuLyXongChonNguoiChi(self):
        ten = layTenDuocChon(self.listChonNguoiChi, WidgetChonMot)
        if not ten:
            QMessageBox.warning(self, "Chua chon", "Vui long chon nguoi chi!"); return
        self.ql.datNguoiChi(ten)
        self.btnNguoiChi.setText(f"\U0001f464 {ten}")
        self.chuyenTrang(self.I_CHI)

    def xuLyXongChonNguoiDuocChi(self):
        ds = layDanhSachTenDuocChon(self.listNguoiDuocChi, WidgetChonNhieu)
        if not ds:
            QMessageBox.warning(self, "Chua chon", "Vui long chon it nhat mot nguoi!"); return
        self.ql.datDanhSachNguoiNhan(ds)
        hienThi = ds[0] if len(ds) == 1 else f"{ds[0]} +{len(ds)-1}"
        self.btnNguoiDuocChi.setText(f"\U0001f465 {hienThi}")
        self.chuyenTrang(self.I_CHI)

    def _moThanhToan(self):
        self.lblTongNo.setText("0d")
        self.btnNguoiTra.setText("Chon nguoi tra")
        self.btnNguoiNhan.setText("Chon nguoi nhan")
        self.chuyenTrang(self.I_TT)

    def _xuLyXongChonTraNhan(self, listWidget, datFn, btnLabel, canhBao):
        ten = layTenDuocChon(listWidget, WidgetChonMot)
        if not ten:
            QMessageBox.warning(self, "Chua chon", canhBao); return
        datFn(ten); btnLabel.setText(f"\U0001f464 {ten}")
        self.lblTongNo.setText(f"{self.ql.layTongNoHienCo():,.0f}d")
        self.chuyenTrang(self.I_TT)

    def xuLyXongChonNguoiTra(self):
        self._xuLyXongChonTraNhan(self.listNguoiTra, self.ql.datNguoiTra,
                                   self.btnNguoiTra, "Vui long chon nguoi tra!")

    def xuLyXongChonNguoiNhan(self):
        self._xuLyXongChonTraNhan(self.listNguoiNhan, self.ql.datNguoiNhan,
                                   self.btnNguoiNhan, "Vui long chon nguoi nhan!")

    def xuLyXongThanhToan(self):
        if self.ql.xacNhanThanhToan():
            QMessageBox.information(self, "Thanh cong", "Da ghi nhan thanh toan!")
            self.chuyenSangTinhNang()
        else:
            QMessageBox.warning(self, "Loi", "Vui long chon nguoi tra va nguoi nhan!")

    def _moLichSu(self):
        self.lblTenNhomHoatDong.setText(self.ql.layTenNhom())
        self.listHoatDong.clear()
        for moTa in (self.ql.layLichSuHoatDong() or ["Chua co hoat dong nao."]):
            self.listHoatDong.addItem(QListWidgetItem(moTa))
        self.chuyenTrang(self.I_LS)

    def _moThongBao(self):
        self.lblTenNhomThongBao.setText(self.ql.layTenNhom())
        self.chuyenTrang(self.I_TBAO)

    def _moThongTin(self):
        info = self.ql.layThongTinNhom()
        if not info: return
        self.lblTenNhomThongTin.setText(info["tenNhom"])
        self.lblTenNhomTTin.setText(info["tenNhom"])
        self.lblViTriTTin.setText(info["viTri"])
        self.lblSoThanhVien.setText(f"{info['soThanhVien']}/{info['soThanhVien']} nguoi")
        self.lblVaiTro.setText("Truong nhom")
        self.lblNgay.setText(info["ngayTao"])
        self.lblTenCuaTruongNhom.setText(info["nguoiTao"])
        self.lblNhomMa.setText(info["maNhom"])
        px = taoQRPixmap(info["maNhom"], self.lblMaQR.width() or 120)
        self.lblMaQR.setPixmap(px)
        self.lblMaQR.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chuyenTrang(self.I_TTIN)

    def _moAI(self):
        self.lblTenNhomAI.setText(self.ql.layTenNhom())
        self.txtHoiAI.clear()
        self.chuyenTrang(self.I_AI)

    def xuLyGuiAI(self):
        ch = self.txtHoiAI.text().strip()
        if not ch:
            QMessageBox.warning(self, "Chua nhap", "Vui long nhap cau hoi!"); return
        self._xuLyAI(ch)

    def _xuLyAI(self, key: str):
        if "toi uu" in key or "chia tien" in key:
            self._moGoiYChiaTien(); return
        from datetime import datetime
        self.lblTenNhomAITraLoi.setText(self.ql.layTenNhom())
        self.lblGioPhut.setText(datetime.now().strftime("%H:%M %d/%m/%Y"))
        LABEL = {
            "tong ket": "Tong ket chi tieu hien tai",
            "no nhieu": "Ai dang no nhieu nhat?",
            "ngan sach": "Canh bao ngan sach",
            "dia diem": "Goi y dia diem an uong/choi tiep theo",
        }
        self.lblCauHoi.setText(LABEL.get(key, key))
        TRA_LOI = {
            "tong ket": self.ql.layTongKetChiTieu,
            "no nhieu": self.ql.layThongTinNoNhieuNhat,
            "dia diem": self.ql.layGoiYDiaDiem,
        }
        ketQua = (TRA_LOI[key]() if key in TRA_LOI
                  else "Tinh nang dang phat trien." if key == "ngan sach"
                  else f"Ban hoi: {key}")
        self.lblCauTraLoi.setText(ketQua)
        self.lblCauTraLoi.setWordWrap(True)
        self.chuyenTrang(self.I_AI_TL)

    def _moGoiYChiaTien(self):
        dsGoiY = self.ql.layGoiYChiaTien()
        trang  = self.AppChiaTien.widget(self.I_GOI_Y)
        cu = trang.findChild(QListWidget, "listGoiYDong")
        if cu: cu.deleteLater()
        lst = QListWidget(trang)
        lst.setObjectName("listGoiYDong")
        lst.setGeometry(10, 90, 340, 430)
        lst.setStyleSheet("background:transparent;border:none;")
        lst.show()
        if not dsGoiY:
            lst.addItem("Khong co khoan no nao!")
            self.chuyenTrang(self.I_GOI_Y); return
        nhom = self.ql.nhomHienTai
        for g in dsGoiY:
            tv = nhom.layThanhVienTheoTen(g["nguoiNo"])
            w  = QWidget(); lo2 = QHBoxLayout(w); lo2.setContentsMargins(8,6,8,6)
            lo2.addWidget(taoAvatar(g["nguoiNo"][0].upper(), tv.mauAvatar if tv else "#999", 30))
            lbl = QLabel(f"{g['nguoiNo']}  ->  {g['nguoiDuocNo']}")
            lbl.setStyleSheet("font-size:12px;color:#BF360C;font-weight:bold;background:transparent;")
            lblT = QLabel(f"{g['soTien']:,.0f}d")
            lblT.setStyleSheet("font-size:13px;color:#E65100;font-weight:bold;background:transparent;")
            lo2.addWidget(lbl,1); lo2.addWidget(lblT)
            w.setStyleSheet("QWidget{background:#FFF3E0;border-radius:10px;margin:3px;}")
            item = QListWidgetItem(); item.setSizeHint(QSize(320,55))
            lst.addItem(item); lst.setItemWidget(item, w)
        self.chuyenTrang(self.I_GOI_Y)

    def _moTuyChon(self):
        self.lblTenNhomTuyChon.setText(self.ql.layTenNhom())
        self.chuyenTrang(self.I_TUY_CHON)

    def _moChinhSua(self):
        if self.ql.nhomHienTai:
            self.txtSuaTenNhom.setText(self.ql.nhomHienTai.tenNhom)
            self.txtSuaViTri.setText(self.ql.nhomHienTai.viTri)
        self.chuyenTrang(self.I_CHINH_SUA)

    def xuLyLuuChinhSua(self):
        ten = self.txtSuaTenNhom.text().strip()
        if not ten or ten == "Nhap...":
            QMessageBox.warning(self, "Loi", "Ten nhom khong duoc trong!"); return
        self.ql.capNhatThongTinNhom(ten,
            self.txtSuaViTri.text().replace("Nhap...","").strip())
        self._moTuyChon()

    def xuLyXoaNhom(self):
        if QMessageBox.question(self, "Xac nhan", "Xoa toan bo du lieu nhom?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            self.ql.xoaNhom()
            self.txtNhapTenNhom.setText("Nhap...")
            self.txtNhapViTri.setText("Nhap...")
            self.chuyenTrang(self.I_KHOI_TAO)

    def _moNhanBan(self):
        if self.ql.nhomHienTai:
            self.lblTenNhomNhanBan.setText(self.ql.nhomHienTai.tenNhom)
        self._moChonNhieu(self.listNhanBanNhom, self.I_NHAN_BAN)

    def xuLyChonTatCaNhanBan(self):
        for i in range(self.listNhanBanNhom.count()):
            w = self.listNhanBanNhom.itemWidget(self.listNhanBanNhom.item(i))
            if isinstance(w, WidgetChonNhieu):
                w.cb.setChecked(True)

    def xuLyXongNhanBan(self):
        ten = self.txtTenNhomMoi.text().strip()
        if not ten or ten == "Nhap...":
            QMessageBox.warning(self, "Loi", "Vui long nhap ten nhom moi!"); return
        ds = layDanhSachTenDuocChon(self.listNhanBanNhom, WidgetChonNhieu)
        if self.ql.nhanBanNhom(ten, ds):
            QMessageBox.information(self, "Thanh cong", f"Da nhan ban thanh '{ten}'!")
            self.chuyenSangTrangChu()
        else:
            QMessageBox.warning(self, "Loi", "Khong the nhan ban!")

    def xuLyXuatBaoCao(self):
        dl = self.ql.layDuLieuBaoCao()
        if not dl:
            QMessageBox.warning(self, "Loi", "Chua co du lieu!"); return
        path, _ = QFileDialog.getSaveFileName(self, "Luu bao cao",
            f"baocao_{dl['tenNhom']}.txt", "Text (*.txt)")
        if not path: return
        gdLines = "\n".join(f"{i}. {g['nguoiChi']} chi {g['soTien']:,.0f}d cho {g['nguoiNhan']} - {g['noiDung']}"
                              for i, g in enumerate(dl["danhSachGiaoDich"], 1))
        tcLines = "\n".join(f"  {t}: {v:,.0f}d" for t, v in dl["tongChiThanhVien"].items())
        gyLines = "\n".join(f"  {g['nguoiNo']} -> {g['nguoiDuocNo']}: {g['soTien']:,.0f}d"
                             for g in dl["goiYChiaTien"])
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"BAO CAO: {dl['tenNhom']} | {dl['ngayTao']} | Tong: {dl['tongChi']:,.0f}d\n\n"
                    f"=== GIAO DICH ===\n{gdLines}\n\n"
                    f"=== TONG CHI TUNG NGUOI ===\n{tcLines}\n\n"
                    f"=== GOI Y CHIA TIEN ===\n{gyLines}\n")
        QMessageBox.information(self, "Thanh cong", f"Da luu: {path}")

    def xuLyXuatAnhPDF(self):
        ds = self.ql.layDanhSachAnhChi()
        if not ds:
            QMessageBox.information(self, "Thong bao", "Chua co anh nao!"); return
        path, _ = QFileDialog.getSaveFileName(self, "Luu PDF", "anh.pdf", "PDF (*.pdf)")
        if not path: return
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(path)
        painter = QPainter(printer)
        r = printer.pageRect(QPrinter.Unit.DevicePixel)
        for i, p in enumerate(ds):
            if i > 0: printer.newPage()
            px = QPixmap(p)
            if not px.isNull():
                painter.drawPixmap(0, 0, px.scaled(int(r.width()), int(r.height()),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation))
        painter.end()
        QMessageBox.information(self, "Thanh cong", f"Da luu: {path}")

    def xuLyNhacNo(self):
        ds = self.ql.layGoiYChiaTien()
        if not ds:
            QMessageBox.information(self, "Nhac no", "Khong co khoan no nao!"); return
        nd = "Danh sach no:\n\n" + "".join(
            f"- {g['nguoiNo']} -> {g['nguoiDuocNo']}: {g['soTien']:,.0f}d\n" for g in ds)
        QMessageBox.information(self, "Nhac no", nd)

def chayUngDung():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    cua = CuaSoChinh()
    cua.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    chayUngDung()
