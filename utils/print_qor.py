""" Gathers statistics from VPR runs, like pack/place/route runtimes and Fmax.
"""
import argparse
import csv
import os
import sys
import subprocess


def scan_runtime(fname):
    """ Find runtime of VPR log (if any), else returns empty str. """
    try:
        with open(fname, 'r') as f:
            for line in f:
                pass

            if not line.startswith('The entire flow of VPR took'):
                return ""

            return str(float(line.split()[6]))
    except FileNotFoundError:
        return ""


def scan_critical(fname):
    """ Find critical path and Fmax from VPR log (if any).

    Returns
    -------
    critical_path : str
        Critical path delay in nsec
    fmax : str
        Fmax in MHz.

    """
    try:
        with open(fname, 'r') as f:
            for line in f:
                if line.startswith('Final critical path delay'):
                    parts = line.split()
                    if len(parts) >= 9:
                        # Final critical path delay (least slack): 16.8182 ns, Fmax: 59.4592 MHz
                        critical_path = float(parts[6])
                        fmax = float(parts[9])
                        return str(critical_path), str(fmax)
                    elif len(parts) == 8 and parts[7].strip() == 'ns':
                        # Final critical path delay (least slack): 17.9735 ns
                        critical_path = float(parts[6])
                        fmax = 1000. / critical_path
                        return str(critical_path), str(fmax)
    except FileNotFoundError:
        pass

    return "", ""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build_dir")

    args = parser.parse_args()

    fields = [
        "path",
        "pack time (sec)",
        "place time (sec)",
        "route time (sec)",
        "t_crit (ns)",
        "Fmax (MHz)",
    ]

    print(
        ''.join(
            subprocess.
            getoutput('git show --oneline -s --decorate --color=never')
        ),
        file=sys.stdout
    )
    w = csv.DictWriter(sys.stdout, fields)
    w.writeheader()
    for root, dirs, files in os.walk(args.build_dir):
        if 'pack.log' in files:
            d = {}

            d['path'] = root
            d['pack time (sec)'] = scan_runtime(os.path.join(root, 'pack.log'))
            d['place time (sec)'] = scan_runtime(
                os.path.join(root, 'place.log')
            )
            d['route time (sec)'] = scan_runtime(
                os.path.join(root, 'route.log')
            )
            d['t_crit (ns)'], d['Fmax (MHz)'] = scan_critical(
                os.path.join(root, 'route.log')
            )

            w.writerow(d)


if __name__ == "__main__":
    main()
