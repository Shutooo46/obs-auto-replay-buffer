import sys
import psutil

SYSTEM_PROCESSES = {
    "system", "registry", "smss.exe", "csrss.exe", "wininit.exe",
    "services.exe", "lsass.exe", "svchost.exe", "explorer.exe",
    "taskhostw.exe", "sihost.exe", "fontdrvhost.exe", "dwm.exe",
    "conhost.exe", "dllhost.exe", "ctfmon.exe", "rundll32.exe",
    "spoolsv.exe", "searchindexer.exe", "wuauclt.exe", "winlogon.exe",
    "audiodg.exe", "msdtc.exe", "sppsvc.exe", "wmiprvse.exe",
    "runtimebroker.exe", "backgroundtaskhost.exe", "applicationframehost.exe",
    "startmenuexperiencehost.exe", "searchhost.exe", "widgets.exe",
    "textinputhost.exe", "systemsettings.exe", "lockapp.exe",
}


def get_processes(keyword: str | None) -> list[str]:
    names = set()
    for p in psutil.process_iter(["name"]):
        try:
            name = p.info["name"]
            if not name:
                continue
            if name.lower() in SYSTEM_PROCESSES:
                continue
            if keyword is None or keyword.lower() in name.lower():
                names.add(name)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return sorted(names, key=lambda x: x.lower())


def main() -> None:
    keyword = sys.argv[1] if len(sys.argv) > 1 else None

    processes = get_processes(keyword)

    if keyword:
        print(f'"{keyword}" を含むプロセス一覧:\n')
    else:
        print("現在起動中のプロセス一覧（システムプロセスを除く）:\n")

    if not processes:
        print("  該当するプロセスが見つかりませんでした。")
    else:
        for name in processes:
            print(f"  {name}")

    print('\nconfig.json の "exe" にコピーして使ってください。')


if __name__ == "__main__":
    main()
