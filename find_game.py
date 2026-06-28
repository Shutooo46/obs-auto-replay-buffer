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
    # Windowsゲームバー・キャプチャ関連
    "gamebarftserver.exe", "gamebar.exe", "gamebarftsever.exe",
    "gameinputsvc.exe", "xboxpcapp.exe", "broadcastbandwidthtest.exe",
    # Steam関連
    "steam.exe", "steamservice.exe", "steamwebhelper.exe",
    "gameoverlayui.exe", "gameoverlayui64.exe",
    # Epic Games関連
    "epicgameslauncher.exe", "epicwebhelper.exe", "eosoverlayrenderer-win64-shipping.exe",
    # EA / Origin関連
    "eadesktop.exe", "eabackgroundservice.exe", "easteamproxy.exe",
    "origin.exe", "originclientservice.exe",
    # Battle.net関連
    "battle.net.exe", "battlenet.exe",
    # Riot Games関連
    "riotclientservices.exe", "riotclientux.exe", "riotclientuxrender.exe",
    # OBS関連
    "obs64.exe", "obs32.exe",
    # Discord関連
    "discord.exe", "discordptb.exe", "discordcanary.exe",
    # NVIDIA関連
    "nvidia share.exe", "nvcontainer.exe", "nvdisplay.container.exe",
    "nvoawrappercache.exe", "nvtelemetrycontainer.exe", "nvspcaps64.exe",
    "nvspcaps.exe", "nvwmi64.exe", "nvxdsync.exe", "nvsphelper64.exe",
    # AMD関連
    "amdow.exe", "radeoninstaller.exe", "amddvr.exe", "amdrsserv.exe",
    # その他常駐系
    "razer synapse.exe", "rzsd.exe",
    "anticheatexpert.exe",
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
