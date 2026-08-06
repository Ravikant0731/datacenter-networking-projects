#!/usr/bin/env python3
"""
Project 1: Subnet Design Calculator (VLSM)
--------------------------------------------
Scenario: A company has HQ, one Branch office, and one Data Center.
Base network: 10.0.0.0/16

We need to carve out subnets of different sizes for each site:
  - HQ:          needs ~500 hosts   (Servers + Users + Management)
  - Branch:      needs ~100 hosts
  - Data Center: needs ~1000 hosts  (largest, split further later)

This script:
  1. Takes a base network + list of required host counts.
  2. Calculates the smallest subnet mask that fits each requirement (VLSM).
  3. Allocates non-overlapping subnets automatically.
  4. Prints a clean table you can put in your project README.
"""

import ipaddress


def smallest_subnet_for_hosts(host_count: int) -> int:
    """Return the smallest prefix length that can fit host_count usable hosts."""
    # +2 accounts for network and broadcast addresses
    needed = host_count + 2
    prefix = 32
    while (2 ** (32 - prefix)) < needed:
        prefix -= 1
    return prefix


def allocate_vlsm(base_network: str, site_requirements: list[tuple[str, int]]):
    """
    site_requirements: list of (site_name, host_count), LARGEST first (VLSM best practice)
    Returns list of (site_name, subnet)
    """
    base = ipaddress.ip_network(base_network)
    available = [base]
    allocations = []

    # VLSM rule: always allocate largest requirement first to avoid fragmentation
    sorted_reqs = sorted(site_requirements, key=lambda x: x[1], reverse=True)

    for site_name, host_count in sorted_reqs:
        prefix = smallest_subnet_for_hosts(host_count)
        allocated = None

        for i, block in enumerate(available):
            if block.prefixlen <= prefix:
                subnets = list(block.subnets(new_prefix=prefix))
                allocated = subnets[0]
                remaining = subnets[1:]
                available.pop(i)
                available.extend(remaining)
                break

        if allocated is None:
            raise ValueError(f"Not enough address space left for {site_name} ({host_count} hosts)")

        allocations.append((site_name, allocated, host_count))

    return allocations


def print_table(allocations):
    print(f"{'Site':<15}{'Subnet':<20}{'Usable Range':<35}{'Hosts Needed':<15}{'Hosts Available'}")
    print("-" * 100)
    for site_name, subnet, needed in allocations:
        hosts = list(subnet.hosts())
        usable_range = f"{hosts[0]} - {hosts[-1]}" if hosts else "N/A"
        available_count = subnet.num_addresses - 2
        print(f"{site_name:<15}{str(subnet):<20}{usable_range:<35}{needed:<15}{available_count}")


if __name__ == "__main__":
    BASE_NETWORK = "10.0.0.0/16"

    # (site_name, hosts_needed)
    requirements = [
        ("DataCenter", 1000),
        ("HQ", 500),
        ("Branch", 100),
    ]

    print(f"Base network: {BASE_NETWORK}\n")
    result = allocate_vlsm(BASE_NETWORK, requirements)
    print_table(result)
