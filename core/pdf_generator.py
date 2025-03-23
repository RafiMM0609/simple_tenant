from typing import List, Literal, TypedDict
import pdfkit
from jinja2 import Environment, PackageLoader, select_autoescape
from datetime import date
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
from reportlab.lib.utils import ImageReader
# from barcode.writer import ImageWriter
# from barcode import Code128
# barcode_type = "code128"

# # Generate a barcode object
# code128 = barcode.get_barcode_class(barcode_type)


def generate_barcodes_to_pdf(
    asset_inventaris: List[str],
):
    pdf_buffer = BytesIO()
    pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=letter)
    x, y = 20, 700
    border_padding = 5

    for asset in asset_inventaris:
        if asset is None or len(asset) < 1:
            continue
        
        barcode_buffer = BytesIO()
        barcode = Code128(asset, writer=ImageWriter())
        barcode.write(barcode_buffer)
        barcode_buffer.seek(0)
        
        
        barcode_image = Image.open(barcode_buffer)

        
        barcode_reader = ImageReader(barcode_image)
        pdf_canvas.drawImage(barcode_reader, x, y, width=145, height=60)

        
        pdf_canvas.setLineWidth(1)
        pdf_canvas.setStrokeColorRGB(0, 0, 0)
        pdf_canvas.rect(
            x - border_padding, 
            y - border_padding, 
            145 + (2 * border_padding), 
            60 + (2 * border_padding)
        )
        
        x += 210

        if x >= 460:
            x = 20
            y -= 80
        
        if y < 20:
            pdf_canvas.showPage()
            x, y = 20, 700

    pdf_canvas.save()
    pdf_buffer.seek(0)
    return pdf_buffer


options_landscape = {
    "page-size": "A4",
    "encoding": "utf-8",
    "orientation": "Landscape",
    "print-media-type": True,
}

options_portrait = {
    "page-size": "A4",
    "encoding": "utf-8",
    "orientation": "Portrait",
    "print-media-type": True,
}

env = Environment(
    loader=PackageLoader("core", "pdf_templates"), autoescape=select_autoescape()
)


class DataBarangDict(TypedDict):
    no: int
    serial_number: str
    jumlah_barang: int
    kondisi_barang: str


def generate_bast_pdf(
    nama_pengirim: str,
    jabatan_pengirim: str,
    alamat_pengirim: str,
    lokasi_pengirim: str,
    nama_penerima: str,
    jabatan_penerima: str,
    alamat_penerima: str,
    lokasi_penerima: str,
    tahun: int,
    data_barang: List[DataBarangDict],
    sign_pengirim_base64: str = "",
    sign_penerima_base64: str = "",
    filepath: str = "test.pdf",
    nama_pengirim_ttd: str = "",
    nama_penerima_ttd: str = "",
) -> str:
    template = env.get_template("bast.html")
    string_pdf = template.render(
        nama_pengirim=nama_pengirim,
        jabatan_pengirim=jabatan_pengirim,
        alamat_pengirim=alamat_pengirim,
        lokasi_pengirim=lokasi_pengirim,
        nama_penerima=nama_penerima,
        jabatan_penerima=jabatan_penerima,
        alamat_penerima=alamat_penerima,
        lokasi_penerima=lokasi_penerima,
        tahun=tahun,
        barang=data_barang,
        sign_pengirim_base64=sign_pengirim_base64,
        sign_penerima_base64=sign_penerima_base64,
        nama_pengirim_ttd=nama_pengirim_ttd,
        nama_penerima_ttd=nama_penerima_ttd,
    )
    pdfkit.from_string(string_pdf, f"./tmp/{filepath}", options=options_portrait)
    return f"./tmp/{filepath}"


class DataBarangChecklistN5(TypedDict):
    no: int
    serial_number: str
    serial_number_baterai: str
    serial_number_charger: str
    serial_number_dus: str
    is_baterai: bool
    is_adaptor: bool
    is_kamera: bool

    is_test_print: bool
    is_nfc: bool
    is_adjust: bool
    is_manual_book: bool
    is_geo_location: bool


class DataBarangChecklistA930(TypedDict):
    no: int
    serial_number: str
    serial_number_baterai: str
    serial_number_charger: str
    serial_number_dus: str
    is_baterai: bool
    is_adaptor: bool
    is_kamera: bool

    is_test_print: bool
    is_nfc: bool
    is_adjust: bool
    is_manual_book: bool
    is_geo_location: bool


def generate_bast_3_lembar_pdf(
    nama_pengirim: str,
    jabatan_pengirim: str,
    alamat_pengirim: str,
    lokasi_pengirim: str,
    nama_penerima: str,
    jabatan_penerima: str,
    alamat_penerima: str,
    lokasi_penerima: str,
    tahun: int,
    data_barang: List[DataBarangDict],
    data_barang_checklist_n5: List[DataBarangChecklistN5],
    data_barang_checklist_a930: List[DataBarangChecklistA930],
    sign_pengirim_base64: str = "",
    sign_penerima_base64: str = "",
    filepath: str = "test.pdf",
    nama_pengirim_ttd: str = "",
    nama_penerima_ttd: str = "",
    nama_witel: str = "",
    nik_pengirim: str = "",
    nik_penerima: str = "",
    tanggal_kirim: date = None,
    nama_kota: str = "",
) -> str:
    template = env.get_template("bast_3_lembar.html")

    dict_hari = {
            "Monday":"Senin",
            "Tuesday":"Selasa",
            "Wednesday":"Rabu",
            "Thursday":"Kamis",
            "Friday":"Jumat",
            "Saturday":"Sabut",
            "Sunday":"Minggu",
        }

    dict_bulan = {
            1:"Januari",
            2:"Februari",
            3:"Maret",
            4:"April",
            5:"Mei",
            6:"Juni",
            7:"Juli",
            8:"Agustus",
            9:"September",
            10:"Oktober",
            11:"November",
            12:"Desember",
        }

    tanggal_bulan_tahun = str(tanggal_kirim.day) + " " + dict_bulan[tanggal_kirim.month] + " " + str(tanggal_kirim.year)
    hari_tanggal_bulan_tahun = dict_hari[tanggal_kirim.strftime("%A")] + ", " + tanggal_bulan_tahun
    
    last_nama_kota = nama_kota
    last_nama_kota = last_nama_kota.upper()
    list_kota = last_nama_kota.split(" ")
    if len(list_kota) > 1 and ("KOTA" in list_kota or "KABUPATEN" in list_kota):
        last_nama_kota = list_kota[1]

    last_nama_kota = last_nama_kota.title()

    string_pdf = template.render(
        nama_pengirim=nama_pengirim,
        jabatan_pengirim=jabatan_pengirim,
        alamat_pengirim=alamat_pengirim,
        lokasi_pengirim=lokasi_pengirim,
        nama_penerima=nama_penerima,
        jabatan_penerima=jabatan_penerima,
        alamat_penerima=alamat_penerima,
        lokasi_penerima=lokasi_penerima,
        tahun=tahun,
        barang=data_barang,
        sign_pengirim_base64=sign_pengirim_base64,
        sign_penerima_base64=sign_penerima_base64,
        nama_pengirim_ttd=nama_pengirim_ttd,
        nama_penerima_ttd=nama_penerima_ttd,
        data_barang_checklist_n5=data_barang_checklist_n5,
        data_barang_checklist_a930=data_barang_checklist_a930,
        nama_witel=nama_witel,
        nik_pengirim=nik_pengirim,
        nik_penerima=nik_penerima,
        tanggal_kirim=tanggal_bulan_tahun,
        hari_tanggal_bulan_tahun=hari_tanggal_bulan_tahun,
        nama_kota=last_nama_kota,
    )
    pdfkit.from_string(string_pdf, f"./tmp/{filepath}", options=options_portrait)
    return f"./tmp/{filepath}"


def generate_bast_3_lembar_penerimaan_pdf(
    nama_pengirim: str,
    jabatan_pengirim: str,
    alamat_pengirim: str,
    lokasi_pengirim: str,
    nama_penerima: str,
    jabatan_penerima: str,
    alamat_penerima: str,
    tahun: int,
    data_barang: List[DataBarangDict],
    data_barang_checklist_n5: List[DataBarangChecklistN5],
    data_barang_checklist_a930: List[DataBarangChecklistA930],
    sign_pengirim_base64: str = "",
    sign_penerima_base64: str = "",
    filepath: str = "test.pdf",
    lokasi_penerima: str = "",
    nik_pengirim: str = "",
    nik_penerima: str = "",
    tanggal_kirim: date = None,
    nama_kota: str = "",
    is_different_user_acceptance: bool = False,
    user_penerima_lain: str = "",
    jabatan_penerima_lain: str = "",
) -> str:
    template = env.get_template("bast_3_lembar_penerimaan.html")

    dict_hari = {
            "Monday":"Senin",
            "Tuesday":"Selasa",
            "Wednesday":"Rabu",
            "Thursday":"Kamis",
            "Friday":"Jumat",
            "Saturday":"Sabut",
            "Sunday":"Minggu",
        }

    dict_bulan = {
            1:"Januari",
            2:"Februari",
            3:"Maret",
            4:"April",
            5:"Mei",
            6:"Juni",
            7:"Juli",
            8:"Agustus",
            9:"September",
            10:"Oktober",
            11:"November",
            12:"Desember",
        }

    tanggal_bulan_tahun = str(tanggal_kirim.day) + " " + dict_bulan[tanggal_kirim.month] + " " + str(tanggal_kirim.year)
    hari_tanggal_bulan_tahun = dict_hari[tanggal_kirim.strftime("%A")] + ", " + tanggal_bulan_tahun
    
    last_nama_kota = nama_kota
    last_nama_kota = last_nama_kota.upper()
    list_kota = last_nama_kota.split(" ")
    if len(list_kota) > 1 and ("KOTA" in list_kota or "KABUPATEN" in list_kota):
        last_nama_kota = list_kota[1]

    last_nama_kota = last_nama_kota.title()

    string_pdf = template.render(
        nama_pengirim=nama_pengirim,
        jabatan_pengirim=jabatan_pengirim,
        alamat_pengirim=alamat_pengirim,
        lokasi_pengirim=lokasi_pengirim,
        nama_penerima=nama_penerima,
        jabatan_penerima=jabatan_penerima,
        alamat_penerima=alamat_penerima,
        tahun=tahun,
        barang=data_barang,
        sign_pengirim_base64=sign_pengirim_base64,
        sign_penerima_base64=sign_penerima_base64,
        data_barang_checklist_n5=data_barang_checklist_n5,
        data_barang_checklist_a930=data_barang_checklist_a930,
        lokasi_penerima=lokasi_penerima,
        nik_pengirim=nik_pengirim,
        nik_penerima=nik_penerima,
        tanggal_kirim=tanggal_bulan_tahun,
        hari_tanggal_bulan_tahun=hari_tanggal_bulan_tahun,
        nama_kota=last_nama_kota,
        is_different_user_acceptance=is_different_user_acceptance,
        user_penerima_lain=user_penerima_lain,
        jabatan_penerima_lain=jabatan_penerima_lain,
    )
    pdfkit.from_string(string_pdf, f"./tmp/{filepath}", options=options_portrait)
    return f"./tmp/{filepath}"

def generate_ba_perangkat_rusak_edc(
    masalah: Literal["Rusak", "Kurang", "Hilang", "Bermasalah"],
    tanggal: str,
    nama_spbu: str,
    alamat_spbu: str,
    tipe_aset: str,
    serial_number: str,
    keterangan: str,
    sign_teknisi_base64: str = "",
    sign_pengawas_spbu_base64: str = "",
    sign_waspang_base64: str = "",
    filepath: str = "test.pdf",
    nama_teknisi: str = "",
    nik_teknisi: str = "",
) -> str:
    template = env.get_template("ba-perangkat-rusak-edc.html")
    string_pdf = template.render(
        masalah=masalah,
        tanggal=tanggal,
        nama_spbu=nama_spbu,
        alamat_spbu=alamat_spbu,
        tipe_aset=tipe_aset,
        serial_number=serial_number,
        keterangan=keterangan,
        sign_teknisi_base64=sign_teknisi_base64,
        sign_pengawas_spbu_base64=sign_pengawas_spbu_base64,
        sign_waspang_base64=sign_waspang_base64,
        nama_teknisi=nama_teknisi,
        nik_teknisi=nik_teknisi,
    )
    pdfkit.from_string(string_pdf, f"./tmp/{filepath}", options=options_portrait)
    return f"./tmp/{filepath}"


class InstalasiPerangkatTypedDict(TypedDict):
    no: int
    serial_number: str
    tipe: str
    pot_edc: str
    status: str


def generate_ba_instalasi_perangkat(
    hari: str,
    tanggal: str,
    bulan: str,
    tahun: str,
    nama: str,
    jabatan: str,
    no_telp_hp: str,
    no_spbu: str,
    alamat_spbu: str,
    type_spbu: str,
    instalasi_perangkat_edc: List[InstalasiPerangkatTypedDict],
    nama_teknisi_telkom: str,
    nik_teknisi_telkom: str,
    sign_teknisi_telkom_base64: str = "",
    sign_pihak_spbu_base64: str = "",
    filepath: str = "test.pdf",
) -> str:
    template = env.get_template("ba-instalasi-perangkat.html")
    string_pdf = template.render(
        hari=hari,
        tanggal=tanggal,
        bulan=bulan,
        tahun=tahun,
        nama=nama,
        jabatan=jabatan,
        no_telp_hp=no_telp_hp,
        no_spbu=no_spbu,
        alamat_spbu=alamat_spbu,
        type_spbu=type_spbu,
        instalasi_perangkat_edc=instalasi_perangkat_edc,
        nama_teknisi_telkom=nama_teknisi_telkom,
        nik_teknisi_telkom=nik_teknisi_telkom,
        sign_teknisi_telkom_base64=sign_teknisi_telkom_base64,
        sign_pihak_spbu_base64=sign_pihak_spbu_base64,
    )
    pdfkit.from_string(string_pdf, f"./tmp/{filepath}", options=options_portrait)
    return f"./tmp/{filepath}"


class DetailDataBarangDict(TypedDict):
    no: str
    id_spbu: str
    nama_perangkat: str
    sn_edc: str
    sn_baterai: str
    sn_adapter: str


class PenyebabKerusakanDict(TypedDict):
    no: str
    penyebab_kerusakan: str


class KronologiKerusakanDict(TypedDict):
    no: str
    kronologi_kerusakan: str


def ba_serah_terima_perangkat_rusak(
    tanggal_penyerahan: date,
    data_barang_rusak: DetailDataBarangDict,
    data_barang_pengganti: DetailDataBarangDict,
    penyebab_kerusakan: str = "",
    kronologi_kerusakan: str = "",
    witel: str = "Witel .....",
    sign_witel_base64: str = "",
    username_witel: str = "",
    nik_user_witel: str = "",
    sign_telkom_akses_base64: str = "",
    username_telkom_akses: str = "",
    nik_user_telkom_akses: str = "",
    sign_telkom_sigma_base64: str = "",
    username_telkom_sigma: str = "",
    nik_user_telkom_sigma: str = "",
    filepath: str = "test.pdf",
) -> str:
    template = env.get_template("ba-serah-terima-perangkat-rusak.html")

    dict_bulan = {
            1:"Januari",
            2:"Februari",
            3:"Maret",
            4:"April",
            5:"Mei",
            6:"Juni",
            7:"Juli",
            8:"Agustus",
            9:"September",
            10:"Oktober",
            11:"November",
            12:"Desember",
        }

    nama_hari_tanggal = str(tanggal_penyerahan.day) + " " + dict_bulan[tanggal_penyerahan.month] + " " + str(tanggal_penyerahan.year)
    string_pdf = template.render(
        # tanggal_penyerahan=tanggal_penyerahan,
        tanggal_penyerahan=nama_hari_tanggal,
        data_barang_rusak_id_spbu=data_barang_rusak["id_spbu"],
        data_barang_rusak_nama_perangkat=data_barang_rusak["nama_perangkat"],
        data_barang_rusak_sn_edc=data_barang_rusak["sn_edc"],
        data_barang_rusak_sn_baterai=data_barang_rusak["sn_baterai"],
        data_barang_rusak_sn_adapter=data_barang_rusak["sn_adapter"],
        data_barang_pengganti_id_spbu=data_barang_pengganti["id_spbu"],
        data_barang_pengganti_nama_perangkat=data_barang_pengganti["nama_perangkat"],
        data_barang_pengganti_sn_edc=data_barang_pengganti["sn_edc"],
        data_barang_pengganti_sn_baterai=data_barang_pengganti["sn_baterai"],
        data_barang_pengganti_sn_adapter=data_barang_pengganti["sn_adapter"],
        penyebab_kerusakan=penyebab_kerusakan,
        kronologi_kerusakan=kronologi_kerusakan,
        witel=witel,
        sign_witel_base64=sign_witel_base64,
        username_witel=username_witel,
        nik_user_witel=nik_user_witel,
        sign_telkom_akses_base64=sign_telkom_akses_base64,
        username_telkom_akses=username_telkom_akses,
        nik_user_telkom_akses=nik_user_telkom_akses,
        sign_telkom_sigma_base64=sign_telkom_sigma_base64,
        username_telkom_sigma=username_telkom_sigma,
        nik_user_telkom_sigma=nik_user_telkom_sigma,
    )
    pdfkit.from_string(string_pdf, f"./tmp/{filepath}", options=options_portrait)
    return f"./tmp/{filepath}"


def ba_serah_terima_perangkat_rusak_v2(
    tanggal_penyerahan: date,
    list_data_barang_rusak: List[DetailDataBarangDict],
    list_data_barang_pengganti: List[DetailDataBarangDict],
    penyebab_kerusakan: List[PenyebabKerusakanDict] = [],
    kronologi_kerusakan: List[KronologiKerusakanDict] = [],
    witel: str = "Witel .....",
    sign_witel_base64: str = "",
    username_witel: str = "",
    nik_user_witel: str = "",
    sign_telkom_akses_base64: str = "",
    username_telkom_akses: str = "",
    nik_user_telkom_akses: str = "",
    sign_telkom_sigma_base64: str = "",
    username_telkom_sigma: str = "",
    nik_user_telkom_sigma: str = "",
    filepath: str = "test.pdf",
) -> str:
    template = env.get_template("ba-serah-terima-perangkat-rusak-v2.html")

    dict_bulan = {
            1:"Januari",
            2:"Februari",
            3:"Maret",
            4:"April",
            5:"Mei",
            6:"Juni",
            7:"Juli",
            8:"Agustus",
            9:"September",
            10:"Oktober",
            11:"November",
            12:"Desember",
        }

    nama_hari_tanggal = str(tanggal_penyerahan.day) + " " + dict_bulan[tanggal_penyerahan.month] + " " + str(tanggal_penyerahan.year)
 
    string_pdf = template.render(
        # tanggal_penyerahan=tanggal_penyerahan,
        tanggal_penyerahan=nama_hari_tanggal,
        data_barang_rusak=list_data_barang_rusak,
        data_barang_pengganti=list_data_barang_pengganti,
        penyebab_kerusakan=penyebab_kerusakan,
        kronologi_kerusakan=kronologi_kerusakan,
        witel=witel,
        sign_witel_base64=sign_witel_base64,
        username_witel=username_witel,
        nik_user_witel=nik_user_witel,
        sign_telkom_akses_base64=sign_telkom_akses_base64,
        username_telkom_akses=username_telkom_akses,
        nik_user_telkom_akses=nik_user_telkom_akses,
        sign_telkom_sigma_base64=sign_telkom_sigma_base64,
        username_telkom_sigma=username_telkom_sigma,
        nik_user_telkom_sigma=nik_user_telkom_sigma,
    )
    pdfkit.from_string(string_pdf, f"./tmp/{filepath}", options=options_portrait)
    return f"./tmp/{filepath}"


class ListDataBarangRelokasi(TypedDict):
    no: str
    serial_number: str
    spbu_awal: str
    spbu_relokasi: str
    tiket: str
    alasan: str


def ba_relokasi(
    tipe_edc: str,
    hari_tanggal: str,
    pic_telkom_akses: str,
    list_data_barang_relokasi: List[ListDataBarangRelokasi],
    tanggal_pengajuan: str,
    sign_spbu_base64: str,
    sign_telkom_akses_base64: str,
    nama_telkom_akses: str,
    nik_telkom_akses: str,
    filepath: str = "test.pdf",
) -> str:
    template = env.get_template("ba-relokasi-edc.html")
    string_pdf = template.render(
        tipe_edc=tipe_edc,
        hari_tanggal=hari_tanggal,
        pic_telkom_akses=pic_telkom_akses,
        list_data_barang_relokasi=list_data_barang_relokasi,
        tanggal_pengajuan=tanggal_pengajuan,
        sign_spbu_base64=sign_spbu_base64,
        sign_telkom_akses_base64=sign_telkom_akses_base64,
        nama_telkom_akses=nama_telkom_akses,
        nik_telkom_akses=nik_telkom_akses,
    )
    pdfkit.from_string(string_pdf, f"./tmp/{filepath}", options=options_portrait)
    return f"./tmp/{filepath}"


class TaskBarangRusakDict(TypedDict):
    nama_spbu: str
    alamat_spbu: str
    tipe_aset: str
    serial_number: str


def generate_ba_all_perangkat_rusak_edc(
    masalah: Literal["Rusak", "Kurang", "Hilang", "Bermasalah"],
    tanggal: str,
    list_task_barang: List[TaskBarangRusakDict],
    keterangan: str,
    sign_teknisi_base64: str = "",
    sign_pengawas_spbu_base64: str = "",
    sign_waspang_base64: str = "",
    filepath: str = "test.pdf",
    nama_teknisi: str = "",
    nik_teknisi: str = "",
) -> str:
    template = env.get_template("ba-perangkat-rusak-all-edc.html")
    string_pdf = template.render(
        masalah=masalah,
        tanggal=tanggal,
        list_task_barang=list_task_barang,
        keterangan=keterangan,
        sign_teknisi_base64=sign_teknisi_base64,
        sign_pengawas_spbu_base64=sign_pengawas_spbu_base64,
        sign_waspang_base64=sign_waspang_base64,
        nama_teknisi=nama_teknisi,
        nik_teknisi=nik_teknisi,
    )
    pdfkit.from_string(string_pdf, f"./tmp/{filepath}", options=options_portrait)
    return f"./tmp/{filepath}"


class DetailDataBarangRelokasiDict(TypedDict):
    no: str
    spbu_awal: str
    spbu_relokasi: str
    alasan: str
    
def generate_ba_relokasi_penarikan_aset(
    tanggal_kirim: date,
    tahun:int,
    barang_relokasi: List[DetailDataBarangRelokasiDict],
    nama_hari: str,
    nama_teknisi_telkom: str,
    nik_teknisi_telkom: str,
    sign_teknisi_telkom_base64: str = "",
    sign_pihak_spbu_base64: str = "",
    filepath: str = "test.pdf", 
    nama_kota: str = "",
    tipe_edc: str = "",
    tanggal_kirim_ttd: str = "",
) -> str:
    template = env.get_template("ba-relokasi-penarikan.html")

    dict_bulan = {
            1:"Januari",
            2:"Februari",
            3:"Maret",
            4:"April",
            5:"Mei",
            6:"Juni",
            7:"Juli",
            8:"Agustus",
            9:"September",
            10:"Oktober",
            11:"November",
            12:"Desember",
        }

    nama_hari_tanggal = str(tanggal_kirim.day) + " " + dict_bulan[tanggal_kirim.month] + " " + str(tanggal_kirim.year)
    
    string_pdf = template.render(
        #tanggal_kirim=tanggal_kirim,
        tanggal_kirim=nama_hari_tanggal,
        barang_relokasi=barang_relokasi,
        nama_hari=nama_hari,
        tahun=tahun,
        nik_teknisi_telkom=nik_teknisi_telkom,
        nama_teknisi_telkom=nama_teknisi_telkom,
        sign_teknisi_telkom_base64=sign_teknisi_telkom_base64,
        sign_pihak_spbu_base64=sign_pihak_spbu_base64,
        nama_kota=nama_kota,
        tipe_edc=tipe_edc,
        tanggal_kirim_ttd=tanggal_kirim_ttd
    )
    pdfkit.from_string(string_pdf, f"./tmp/{filepath}", options=options_portrait)
    return f"./tmp/{filepath}"


class RelokasiInstalasiTypedDict(TypedDict):
    no: int
    serial_number: str
    tipe: str
    pot_edc: str
    status: str

def generate_ba_relokasi_instalasi_aset(
    no_urut_relokasi_instalasi: str,
    hari: str,
    tanggal: str,
    bulan: str,
    tahun: str,
    nama: str,
    jabatan: str,
    no_telp_hp: str,
    no_spbu: str,
    alamat_spbu: str,
    type_spbu: str,
    list_instalasi_relokasi_aset: List[RelokasiInstalasiTypedDict],
    nama_teknisi_telkom: str,
    nik_teknisi_telkom: str,
    sign_teknisi_telkom_base64: str = "",
    sign_pihak_spbu_base64: str = "",
    filepath: str = "test.pdf",
) -> str:
    template = env.get_template("ba-relokasi-instalasi.html")
    string_pdf = template.render(
        no_urut_relokasi_instalasi=no_urut_relokasi_instalasi,
        hari=hari,
        tanggal=tanggal,
        bulan=bulan,
        tahun=tahun,
        nama=nama,
        jabatan=jabatan,
        no_telp_hp=no_telp_hp,
        no_spbu=no_spbu,
        alamat_spbu=alamat_spbu,
        type_spbu=type_spbu,
        list_instalasi_relokasi_aset=list_instalasi_relokasi_aset,
        nama_teknisi_telkom=nama_teknisi_telkom,
        nik_teknisi_telkom=nik_teknisi_telkom,
        sign_teknisi_telkom_base64=sign_teknisi_telkom_base64,
        sign_pihak_spbu_base64=sign_pihak_spbu_base64,
    )
    pdfkit.from_string(string_pdf, f"./tmp/{filepath}", options=options_portrait)
    return f"./tmp/{filepath}"

class DetailChecklist(TypedDict):
    nama: str
    is_ok: bool


class ChecklistDataBarangtN5(TypedDict):
    no: int
    serial_number: str
    serial_number_baterai: str
    serial_number_charger: str
    checklist: list[DetailChecklist]


class ChecklistDataBarangA930(TypedDict):
    no: int
    serial_number: str
    serial_number_baterai: str
    serial_number_charger: str
    checklist: list[DetailChecklist]


def generate_ba_checklist_qc_witel(
    witel: str,
    alamat: str,
    tanggal: date,
    data_barang_checklist_n5: List[ChecklistDataBarangtN5],
    data_barang_checklist_a930: List[ChecklistDataBarangA930],
    nama_user_qc_witel: str = "",
    nik_user_qc_witel: str = "",
    sign_user_qc_witel_base64: str = "",
    nama_user_qc_telkom_akses: str = "",
    nik_user_qc_telkom_akses: str = "",
    sign_user_qc_telkom_akses_base64: str = "",
    filepath: str = "test.pdf",
) -> str:
    template = env.get_template("ba-checklist-qc-witel.html")
    # Get All checklist N5
    all_checklist_n5: list[str] = []
    for x in data_barang_checklist_n5:
        all_checklist_n5 += [y["nama"] for y in x["checklist"]]
    unique_all_checklist_n5 = list(set(all_checklist_n5))
    all_checklist_n5 = sorted(unique_all_checklist_n5)

    for x in data_barang_checklist_n5:
        for required_checklist in all_checklist_n5:
            if required_checklist not in [z["nama"] for z in x["checklist"]]:
                x["checklist"].append({"nama": required_checklist, "is_ok": False})

        new_checklist = []
        for checklist in x["checklist"]:
            if checklist["nama"] in all_checklist_n5:
                new_checklist.append(checklist)
        new_checklist = sorted(new_checklist, key=lambda d: d["nama"])
        x["checklist"] = [z["is_ok"] for z in new_checklist]

    # Get All checklist A930
    all_checklist_a930: list[str] = []
    for x in data_barang_checklist_a930:
        all_checklist_a930 += [y["nama"] for y in x["checklist"]]
    unique_all_checklist_a930 = list(set(all_checklist_a930))
    all_checklist_a930 = sorted(unique_all_checklist_a930)

    for x in data_barang_checklist_a930:
        for required_checklist in all_checklist_a930:
            if required_checklist not in [z["nama"] for z in x["checklist"]]:
                x["checklist"].append({"nama": required_checklist, "is_ok": False})

        new_checklist = []
        for checklist in x["checklist"]:
            if checklist["nama"] in all_checklist_a930:
                new_checklist.append(checklist)
        new_checklist = sorted(new_checklist, key=lambda d: d["nama"])
        x["checklist"] = [z["is_ok"] for z in new_checklist]

    # add number
    for no, x in enumerate(data_barang_checklist_n5, start=1):
        x["no"] = no

    for no, x in enumerate(data_barang_checklist_a930, start=1):
        x["no"] = no

    dict_hari = {
            "Monday":"Senin",
            "Tuesday":"Selasa",
            "Wednesday":"Rabu",
            "Thursday":"Kamis",
            "Friday":"Jumat",
            "Saturday":"Sabut",
            "Sunday":"Minggu",
        }

    dict_bulan = {
            1:"Januari",
            2:"Februari",
            3:"Maret",
            4:"April",
            5:"Mei",
            6:"Juni",
            7:"Juli",
            8:"Agustus",
            9:"September",
            10:"Oktober",
            11:"November",
            12:"Desember",
        }

    tmp_tanggal = str(tanggal.day) + " " + dict_bulan[tanggal.month] + " " + str(tanggal.year)
    tanggal_nama_hari = dict_hari[tanggal.strftime("%A")] + ", " + tmp_tanggal

    string_pdf = template.render(
        witel=witel,
        alamat=alamat,
        tanggal=tanggal_nama_hari,
        nama_user_qc_witel = nama_user_qc_witel,
        nik_user_qc_witel = nik_user_qc_witel,
        sign_user_qc_witel_base64 = sign_user_qc_witel_base64,
        nama_user_qc_telkom_akses = nama_user_qc_telkom_akses,
        nik_user_qc_telkom_akses = nik_user_qc_telkom_akses,
        sign_user_qc_telkom_akses_base64 = sign_user_qc_telkom_akses_base64,
        cheklist_n5=all_checklist_n5,
        cheklist_a930=all_checklist_a930,
        data_barang_checklist_n5=data_barang_checklist_n5,
        data_barang_checklist_a930=data_barang_checklist_a930,
    )
    pdfkit.from_string(string_pdf, f"./tmp/{filepath}", options=options_landscape)
    return f"./tmp/{filepath}"


def generate_ba_kehilangan_aset(
    nama_pic_spbu: str = "",
    jabatan_pic_spbu: str = "",
    jenis_barang: str = "",
    merek_barang: str = "",
    tipe_barang: str = "",
    serial_number: str = "",
    keterangan: str = "",
    nama_kota : str = "",
    nama_hari: str = "",
    tanggal_bulan_tahun: str = "",
    sign_teknisi_base64: str = "",
    sign_pengawas_spbu_base64: str = "",
    sign_witel_base64: str = "",
    nama_petugas_witel: str = "",
    nik_petugas_witel: str = "",
    nama_petugas_telkomakses: str = "",
    nik_petugas_telkomakses: str = "",
    filepath: str = "test.pdf", 
):
    template = env.get_template("ba-kehilangan-perangkat.html")

    last_nama_kota = nama_kota
    last_nama_kota = last_nama_kota.upper()
    list_kota = last_nama_kota.split(" ")
    if len(list_kota) > 1 and ("KOTA" in list_kota or "KABUPATEN" in list_kota):
        last_nama_kota = list_kota[1]

    last_nama_kota = last_nama_kota.title()

    string_pdf = template.render(
        nama_pic_spbu = nama_pic_spbu,
        jabatan_pic_spbu = jabatan_pic_spbu,
        jenis_barang = jenis_barang,
        merek_barang = merek_barang,
        tipe_barang = tipe_barang,
        serial_number = serial_number,
        nama_kota = last_nama_kota,
        keterangan = keterangan,
        nama_hari = nama_hari,
        tanggal_bulan_tahun = tanggal_bulan_tahun,
        sign_teknisi_base64 = sign_teknisi_base64,
        sign_pengawas_spbu_base64 = sign_pengawas_spbu_base64,
        nama_petugas_witel = nama_petugas_witel,
        sign_witel_base64 = sign_witel_base64,
        nik_petugas_witel = nik_petugas_witel,
        nama_petugas_telkomakses = nama_petugas_telkomakses,
        nik_peugas_telkomakses = nik_petugas_telkomakses,
    )

    pdfkit.from_string(string_pdf, f"./tmp/{filepath}", options=options_portrait)
    return f"./tmp/{filepath}"
