# Module CLI Configurator

Desktop app cau hinh module qua CLI text, viet bang Python 3.11+, PySide6 va pyserial.

## Cai dat

```bash
pip install -r requirements.txt
```

## Chay ung dung

```bash
python main.py
```

## Su dung nhanh

- Chon `MOCK` trong dropdown COM Port de test khong can hardware.
- Bam `Refresh` de quet lai cong COM.
- Bam `Connect`, sau do dung `Read` hoac `View` de gui lenh `pl`.
- Dung combobox `Setup TX` / `Setup RX` trong panel trai de chuyen nhom tham so can cau hinh.
- Sua tham so trong panel trai, bam `Save` de chi gui cac parameter da thay doi bang cu phap `p key=value;`.
- Khi save, app gui tung lenh cach nhau 50ms. Lenh cuoi cung luon la `pstore;`.
- Bam `Version` de gui lenh `v`.
- Nhap lenh CLI bat ky o o duoi cung va nhan Enter.
- `Reboot` se hien dialog xac nhan truoc khi gui `reboot`.

## Cau truc

```text
core/
  cli_parser.py       Parser key=value va build lenh set
  config_schema.py    Dinh nghia parameter module
  config_store.py     Luu/cap nhat JSON local, import/export
serial/
  serial_manager.py   Quan ly pyserial, QThread va mock backend
ui/
  main_window.py      MainWindow va signal/slot dieu phoi app
  styles.py           Dark stylesheet
widgets/
  config_widget.py    Form cau hinh co search/favorite/change tracking
  log_viewer.py       Terminal log TX/RX/ERROR/INFO co timestamp
  telemetry_widget.py Telemetry panel mo phong realtime
main.py               Entry point
```

## Lenh CLI duoc ho tro

App giao tiep qua text CLI:

```text
p tx_power=0;
p rf_band=0;
p tx_ch_source=2;
p bind_phrase=my_phrase;
p mode=0;
p tx_ch_order=0;
p tx_ser_dest=0;
p tx_power_sw_ch=0;
p tx_ser_baudrate=4;
p tx_snd_radiostat=0;
p TX_MAV_COMPONENT=1;
p RF_Ortho=0;
p rx_power=0;
p RX_OUT_MODE=0;
p rx_ser_baudrate=4;
p RX_SER_LINK_MODE=1;
p Rx_Snd_RadioStat=0;
p Rx_Ser_Port=0;
p RX_SND_RCCHANNEL=0;
p RX_OUT_RSSI_CH=0;
p RX_OUT_LQ_CH=0;
p rx_power_sw_ch=0;
pstore;
pl;
v;
reboot;
```

Du lieu tra ve dang `KEY=VALUE` hoac `p KEY=VALUE;` se duoc parse va cap nhat GUI neu trung parameter da khai bao.

## MAVLink telemetry dang doc

Panel telemetry doc cac message text sau neu module forward ra serial:

```text
HEARTBEAT
ATTITUDE
LOCAL_POSITION_NED
GLOBAL_POSITION_INT
RAW_IMU
SYS_STATUS
VFR_HUD
PARAM_VALUE
```

Vi du format duoc ho tro:

```text
ATTITUDE roll=0.1 pitch=-0.2 yaw=1.57
GLOBAL_POSITION_INT lat=107769000 lon=1067009000 alt=30500 relative_alt=10200 hdg=9000
SYS_STATUS voltage_battery=12150 current_battery=145 battery_remaining=86
```
