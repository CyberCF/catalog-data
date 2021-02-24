#!  /usr/bin/env python3
__author__ = "Donald Wolfson"
__email__ = "dwolfson@zeus.caida.org"
# This software is Copyright (C) 2020 The Regents of the University of
# California. All Rights Reserved. Permission to copy, modify, and
# distribute this software and its documentation for educational, research
# and non-profit purposes, without fee, and without a written agreement is
# hereby granted, provided that the above copyright notice, this paragraph
# and the following three paragraphs appear in all copies. Permission to
# make commercial use of this software may be obtained by contacting:
#
# Office of Innovation and Commercialization
#
# 9500 Gilman Drive, Mail Code 0910
#
# University of California
#
# La Jolla, CA 92093-0910
#
# (858) 534-5815
#
# invent@ucsd.edu
#
# This software program and documentation are copyrighted by The Regents of
# the University of California. The software program and documentation are
# supplied “as is”, without any accompanying services from The Regents. The
# Regents does not warrant that the operation of the program will be
# uninterrupted or error-free. The end-user understands that the program
# was developed for research purposes and is advised not to rely
# exclusively on the program for any reason.
#
# IN NO EVENT SHALL THE UNIVERSITY OF CALIFORNIA BE LIABLE TO ANY PARTY FOR
# DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES,
# INCLUDING LOST PR OFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS
# DOCUMENTATION, EVEN IF THE UNIVERSITY OF CALIFORNIA HAS BEEN ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE. THE UNIVERSITY OF CALIFORNIA SPECIFICALLY
# DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
# SOFTWARE PROVIDED HEREUNDER IS ON AN “AS IS” BASIS, AND THE UNIVERSITY OF
# CALIFORNIA HAS NO OBLIGATIONS TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
# ENHANCEMENTS, OR MODIFICATIONS.

################################## Imports #####################################

import argparse
import difflib
import json
import sys
import re
import os

#################################### Header ####################################

"""
    This script will create unique JSON objects based on metadata stored in the
    YAML file, data/data-papers.yaml. Each paper found is parsed for its TOPKEYS
    which map to manually inputted data about the paper. This script produces
    objects for papers, software, and media. Each new object is writted to its
    respective directory with the tag __externallinks.json.
"""

############################## Global Variables ################################

# Datasets
seen_papers = set()     # Will hold all found paper IDs.
seen_authors = set()    # Will hold all found author IDs.
author_data = {}        # Will map all authors IDs to their JSON.
papers = {}             # Will hold each paper.     

# Definitions
topkeys = {
    "MARKER",
    "TYPE",
    "AUTHOR",
    "GEOLOC",
    "TITLE",
    "YEAR",
    "TOPKEY",
    "SERIAL",
    "VOLUME",
    "CHAPTER",
    "ARTICLE",
    "PAGE",
    "CTITLE",
    "DOI",
    "URL",
    "ABS",
    "PLACE",
    "PUBLISH",
    "REMARK"
}
topkey_2_dataset = {
  # "Anonymized Internet Traces -> traces"
  "passive-stats"                     : "passive_metadata",
  "passive-realtime"                  : "passive_realtime",
  "passive-generic"                   : "passive_generic",
  "passive-ipv6day-and-ipv6launch"    : "passive_ipv6launch_pcap",
  "passive-oc48"                      : "passive_oc48_pcap",
  "passive-2007"                      : "passive_2007_pcap",
  "passive-2008"                      : "passive_2008_pcap",
  "passive-2009"                      : "passive_2009_pcap",
  "passive-2010"                      : "passive_2010_pcap",
  "passive-2011"                      : "passive_2011_pcap",
  "passive-2012"                      : "passive_2012_pcap",
  "passive-2013"                      : "passive_2013_pcap",
  "passive-2014"                      : "passive_2014_pcap",
  "passive-2015"                      : "passive_2015_pcap",
  "passive-2016"                      : "passive_2016_pcap",
  "passive-2017"                      : "passive_2017_pcap",
  "passive-2018"                      : "passive_2018_pcap",
  "passive-2019"                      : "passive_2019_pcap",

  # "Topology with Archipelago -> ark"
  "topology-generic"                  : "software:archipelago",
  "topology-ark-ipv4-traceroute"      : "ipv4_routed_24_topology",
  "topology-ark-ipv6-traceroute"      : "ipv6_allpref_topology",
  "topology-ark-itdk"                 : "internet-topology-data-kit",
  "topology-itdk"                     : "internet-topology-data-kit",
  "topology-ark-ipv4-prefix-probing"  : "ipv4_prefix_probing_dataset",
  "topology-ark-ipv4-aslinks"         : "ipv4_routed_topology_aslinks",
  "topology-ark-ipv6-aslinks"         : "ipv6_aslinks",
  "topology-ark-ipv6-routed48"        : "ipv6_allpref_topology",
  "topology-ark-ipv6_traceroute"      : "ipv6_allpref_topology",
  "topology-ark-dnsnames"             : ["ipv4_dnsnames","ipv6_dnsnames"],
  "topology-ark-dns-names"            : ["ipv4_dnsnames","ipv6_dnsnames"], 
  "topology-ark-tod"                  : "software:vela",
  "topology-ark-activity"             : "software:archipelago",
  "topology-ark-vela"                 : "software:vela",

  # "Topology with Skitter -> skitter"
  "topology-skitter-ipv4"             : "skitter_internet_topology_data_kit",
  "topology-skitter-itdk"             : "skitter_internet_topology_data_kit",
  "topology-skitter-aslinks"          : "skitter_aslinks_dataset",
  "topology-skitter-rlinks"           : "skitter_macroscopic_topology_data",
  "skitter-router-adjacencies"        : "skitter_router_level_topology_measurements",

  # "Topology with BGP -> bgp"
  "topology-as-relationships"         : "as_relationships",
  "topology-as-classification"        : "as_classification",
  "topology-as-organization"          : "as_organization",
  "as-organizations"                  : "as_organization",
  "topology-as-rank"                  : "asrank",
  "routeviews-generic"                : "as_prefix",
  "routeviews-prefix2as"              : "as_prefix",

  # "UCSD Network Telescope -> telescope"
  "telescope-generic"                 : "ucsd_network_telescope",
  "telescope-2days-2008"              : "telescope_anon_twodays",
  "telescope-3days-conficker"         : "telescope_anon_conficker",
  "telescope-sipscan"                 : "telescope_sipscan",
  "telescope-patch-tuesday"           : "corsaro_patch_tuesday",
  "telescope-educational"             : "telescope_educational",
  "telescope-real-time"               : "ucsd_network_telescope",
  "backscatter-generic"               : "telescope_backscatter",
  "backscatter-tocs"                  : "backscatter_tocs_originals",
  "backscatter-2004-2005"             : "telescope_backscatter",
  "backscatter-2006"                  : "telescope_backscatter",
  "backscatter-2007"                  : "telescope_backscatter",
  "backscatter-2008"                  : "telescope_backscatter",
  "backscatter-2009"                  : "telescope_backscatter",
  "witty worm"                        : "telescope_witty_worm",
  "code-red worm"                     : "telescope_codered_worm",

  # "Denial of Service Attacks -> ddos"
  "ddos-generic"                      : "telescope_ddos",
  "ddos-20070804"                     : "ddos-attack-2007",
  "ddos-20070806"                     : "ddos-attack-2007",

  # "Other Datasets -> other"
  "dns-rtt-generic"                   : "software:dnsstat",
  "dns-root-gtld-rtt"                 : "dns_root_gtld_rtt",
  "peeringdb"                         : "peeringdb_archive",
  "ixps"                              : "ixps",
  "spoofer"                           : "spoofer",

  # "Paper Data and Tools -> paper"
  "complex_as_relationships"          : "paper:2014_inferring_complex_as_relationships",
  "2006-pam-as-taxonomy"              : "2006_pam_as_taxonomy",
  "2016-periscope"                    : "software:periscope_looking_glass_api",
  "2013-midar"                        : "software:midar",
  "bgpstream"                         : "software:bgpstream",
  "scamper"                           : "software:scamper",
  "iffinder"                          : "software:iffinder",
  "mapnet"                            : "software:mapnet",
  "coralreef"                         : "software:coralreef",
  "datcat"                            : "software:datcat",
  "dolphin"                           : "media:2014_dolphin_bulk_dns_resolution_tool",
  "asfinder"                          : "software:coralreef",
  "netgeo"                            : "software:netgeo",
  "ioda"                              : "software:ioda"
}
alternate_links = ["software:", "media:", "paper:"]
re_yml = re.compile(r".yaml")
re_jsn = re.compile(r".json")
re_pbd = re.compile(r"__pubdb")

# File Paths
data_papers = None

################################# Main Method ##################################

def main(argv):
    global seen_papers
    global seen_authors
    global author_data
    global papers
    global topkeys
    global topkey_2_dataset
    global alternate_links
    global re_yml
    global re_jsn
    global re_pbd
    global data_papers

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", type=str, default=None, dest="data_papers", help="Path to data-papers.yaml")
    args = parser.parse_args()

    # Edge Case: Exit if no data_papers is given.
    if args.data_papers is None:
        sys.exit()

    data_papers = args.data_papers

    # Update seen_papers with papers currently in sources/paper/
    update_seen_papers()

    # Update author_data with all authors found in sources/person/
    update_author_data()

    # Parse data_papers and create a new file for each paper.
    parse_data_papers()

    # Print all the papers found to their respective JSON files.
    print_papers()

    # Print all the papers found to their respective JSON files.
    print_authors()

############################### Helper Methods #################################

# Add each paper's ID to seen_papers from the source/paper directory.
def update_seen_papers():
    global seen_papers

    for file in os.listdir("sources/paper"):
        # Edge Case: Skip if file is not .json and excludes __pubdb from name.
        if not re_jsn.search(file) and not re_pbd.search(file):
            continue

        file = file.split("__")[0]
        seen_papers.add(file)


# Add each author's JSON data to author_data.
def update_author_data():
    global seen_authors
    global author_data

    for file in os.listdir("sources/person"):
        # Edge Case: Skip if file is not .json.
        if not re_jsn.search(file):
            continue

        # Open the file and save its data.
        file = "sources/person/{}".format(file)
        with open(file, "r") as opened_file:
            data = json.load(opened_file)
        
        # Store the author's data.
        author_name = data["id"].split(":")[1]
        author_data[author_name] = data
        seen_authors.add(author_name)


# Opens a give .yaml file and parses each paper listed between delimeters.
def parse_data_papers():
    global re_yml
    global data_papers
    global topkeys

    # Parse data_papers file.
    if re_yml.search(data_papers):
        with open(data_papers, "r") as file:
            # Will store all the data for the current paper.
            curr_paper = ""
            curr_line = file.readline()
            while curr_line:
                # Edge Case: Skip commented lines.
                if curr_line[0] == "#":
                    curr_line = file.readline()
                    continue

                # Base Case: Parse current paper once delimeter is found.
                if "---" in curr_line:
                    if len(curr_paper) != 0:
                        parse_paper(curr_paper)
                    curr_paper = ""
                    curr_line = file.readline()
                    continue
                
                # Check if the current line has one of the TOPKEY values.
                topkey_in_line = False
                for topkey in topkeys:
                    if topkey in curr_line:
                        topkey_in_line = True
                
                # Strip newline characters from lines without TOPKEY values.
                if not topkey_in_line:
                    curr_paper = curr_paper.rstrip()
                    curr_paper += curr_line.strip()
                else:
                    curr_paper += curr_line.lstrip()
                curr_line = file.readline()

    # Edge Case: Exit if a given file couldn't be open.
    else:
        print("File must be a .yaml file to be opened.", file=sys.stderr)
        sys.exit()


# Pull out all necessary meta data from the given paper and print a JSON file.
#   @input curr_paper: A string where each \n is another TOPKEY.
def parse_paper(curr_paper):
    global author_data
    global type_2_bibtex
    global papers
    global alternate_links

    # Dictionary that will be printed as a JSON.
    paper = {
        "__typename":"paper",
        "type":"paper",
        "authors":[],
        "bibtextFields":{},
        "links":[],
        "resources":[],
    }

    # Split the current paper into each line.
    curr_paper = curr_paper.split("\n")
    
    # Iterate over each line of the current paper.
    for line in curr_paper:
        # Split the current line between the TOPKEY, and its value.
        line = line.split(":")

        # Edge Case: Skip empty lines.
        if len(line) <= 1:
            continue
        
        # Remove any whitespace, and the quotes around the data.
        line[1] = ":".join(map(str, line[1:]))
        line[1] = line[1].replace('"',"").strip()

        # Check which TOPKEY is used for the current line.
        if "MARKER" in line[0]:
            name = line[1].replace(" ", "")

            # Edge Case: Skip seen or repeated papers.
            if name in seen_papers or name in papers:
                return

            paper["id"] = name

            year = line[1][:4]
            bibtext = "https://www.caida.org/publications/papers/{}/{}/bibtex.html".format(year, name[5:])
            paper["resources"].append({
                "name":"bibtex",
                "url":bibtext
            })  
                    
        elif "TYPE" in line[0]:
            paper_type = line[1]
            paper["bibtextFields"]["type"] = paper_type

        elif "AUTHOR" in line[0]:
            # Handle the two seperate ways that authors can be stored.
            authors = line[1]

            # Author's are either split by semicolon, or last name initial.
            if ";" in line[1]:
                authors = authors.split(";")
            else:
                authors = authors.split(".,")

            # Iterate over each author and add there an object for them.
            for author in authors:
                author = author.strip()
                author = re.split(r"\W+", author)
                
                # Format author's name into ID format.
                author_id = ""
                for name_part in author:
                    if len(name_part) >= 1:
                        author_id += "{}__".format(name_part)
                author_id = author_id[:-2]

                paper["authors"].append({
                    "person":"person:{}".format(author_id)
                })

                # Add missing authors to author_data.
                if author_id not in author_data:
                    add_author(author_id)
                    
        elif "GEOLOC" in line[0]:
            locations = line[1].split(";")

            # Edge Case: Apply the single location to all authors.
            if len(locations) == 1 and len(paper["authors"]) != 1:
                location = locations[0].strip()
                for author in paper["authors"]:
                    author_id = author["person"].split(":")[1]
                    add_author_data(author_id, location)
                continue
            
            # Iterate over each location and author object.
            for location, author in zip(locations, paper["authors"]):
                author_id = author["person"].split(":")[1]
                add_author_data(author_id, location.strip())

        elif "TITLE" in line[0] and "CTITLE" not in line[0]:
            title = line[1]
            paper["name"] = title

        elif "YEAR" in line[0]:
            date = line[1].replace("-",".").replace("_",".")
            paper["datePublished"] = date
            paper["date"] = date
            dates = date.split(".")
            paper["bibtextFields"]["year"] = dates[0]
            if len(dates) == 2:
                paper["bibtextFields"]["month"] = dates[1]
        
        elif "TOPKEY" in line[0]:
            datasets = line[1].split(",")

            # Iterate over each dataset and link them to catalog datasets.
            for dataset in datasets:
                # Remove any whitespace.
                dataset = dataset.strip().lower()

                # Try to map the current dataset to a catalog dataset.
                if dataset in topkey_2_dataset:
                    dataset = topkey_2_dataset[dataset]
                elif len(dataset) == 0:
                    continue
                elif dataset.replace(" ", "-") in topkey_2_dataset:
                    dataset = topkey_2_dataset[dataset.replace(" ", "-")]
                elif dataset.replace("_", "-") in topkey_2_dataset:
                    dataset = topkey_2_dataset[dataset.replace("_", "-")]
                else:
                    keys = topkey_2_dataset.keys()
                    closest_match = difflib.get_close_matches(dataset, keys, 1)
                   
                    # Edge Case: Reverse the dataset if no match, then give up.
                    if len(closest_match) == 0:
                        dataset = dataset.replace(" ", "-").replace("_", "-")
                        dataset = dataset.split("-")
                        dataset.reverse()
                        dataset = "-".join(map(str, dataset))
                        if dataset in topkey_2_dataset:
                            dataset = topkey_2_dataset[dataset]
                        else:
                            continue
                    else:
                        dataset = topkey_2_dataset[closest_match[0]]


                # Append link to the dataset.
                alternate_link = False
                for alternate in alternate_links:
                    if alternate in dataset:
                        paper["links"].append({
                            "to":"{}".format(dataset)
                        })
                        alternate_link = True

                # So long as the dataset isn't an alternate link, add it.
                if not alternate_link:
                    # Edge Case: Handles datasets that are mapped to lists.
                    if type(dataset) is list:
                        for data in dataset:
                            paper["links"].append({
                                "to":"dataset:{}".format(data)
                            })
                    else:
                        paper["links"].append({
                            "to":"dataset:{}".format(dataset)
                        })

        elif "SERIAL" in line[0]:
            publisher = line[1]
            paper["publisher"] = publisher
            paper["bibtextFields"]["journal"] = publisher

        elif "VOLUME" in line[0]:
            volume = line[1]
            paper["bibtextFields"]["volume"] = volume
        
        elif "CHAPTER" in line[0] or "ARTICLE" in line[0]:
            number = line[1]
            paper["number"] = number

        elif "PAGE" in line[0]:
            pages = line[1].replace("(", "").replace(")", "")
            paper["pages"] = pages
            paper["bibtextFields"]["pages"] = pages

        elif "CTITLE" in line[0]:
            conference_title = line[1] 
            paper["publisher"] = conference_title
            paper["bibtextFields"]["bookTitle"] = conference_title

        elif "DOI" in line[0]:
            doi = line[1]
            paper["resources"].append({
                "name":"DOI",
                "doi":doi
            })

        elif "URL" in line[0]:
            url = line[1]
            paper["resources"].append({
                "name":"URL",
                "url":url
            })

        elif "ABS" in line[0]:
            paper["description"] = line[1]

        elif "PUBLISH" in line[0]:
            paper["bibtextFields"]["institutions"] = line[1]
        
        elif "REMARK" in line[0] or "PLACE" in line[0]:
            if "annotation" not in paper or len(paper["annotation"]) != 0:
                paper["annotation"] = line[1]
            else:
                paper["annotation"] += " {}".format(line[1])

    # Only add papers that have ID.
    if "id" in paper:
        papers[paper["id"]] = paper


# Helper function to update author_data.
#   @input author_id: The formatted ID for the current author.
#   @input location: The organization that will be added.
#   @return author_orgs: The list of this author's organizations.
def add_author_data(author_id, organization):
    global author_data

    # Add author from author_data, else the current location.
    if author_id in author_data and "organization" in author_data[author_id]:
        # Edge Case: Add the current or to org if missing.
        if organization not in author_data[author_id]["organization"]:
            author_obj = author_data[author_id]
            author_obj["organization"].append(organization)
    else:
        # Add the author to author_data
        add_author(author_id)
        # Add the organization.
        author_data[author_id]["organization"].append(organization)

    return author_data[author_id]["organization"]


# Helper function add an author to author_data.
#   @input author_id: The formatted ID for the current author.
def add_author(author_id):
    global author_data

    # Add the author to author_data
    name = author_id.split("__")
    first_name = name[-1]
    last_name = " ".join(map(str, name[:-1]))
    file_path = "sources/person/{}__externallinks.json".format(author_id)

    author_data[author_id] = {
        "id":"person:{}".format(author_id),
        "__typename":"person",
        "filename":file_path,
        "nameLast":last_name,
        "nameFirst":first_name,
        "organization":[]
    }


# Print each paper to their respective JSON files.
def print_papers():
    global author_data
    global papers

    # Iterate over each paper and print their JSON.
    for paper_id in papers:
        paper = papers[paper_id]
        
        # Update any author data incase new organizations were added.
        for author_object in paper["authors"]:
            author_id = author_object["person"].split(":")[1]
            author_orgs = author_data[author_id]["organization"]
            author_object["organizations"] = author_orgs
        
        # Create a new file for each paper.
        file_path = "sources/paper/{}__externallinks.json".format(paper_id)
        with open(file_path, "w") as paper_file:
            print(json.dumps(paper, indent=4), file=paper_file)


# Print each author to their respective JSON files.
def print_authors():
    global seen_authors
    global author_data

    # Iterate over each author and print their JSON.
    for author_id in author_data:
        author = author_data[author_id]

        # Edge Case: Skip updating author objects that already exist.
        if author_id in seen_authors:
            continue

        if "filename" in author:
            file_path = author["filename"]
        else:
            file_path = "sources/person/{}__externallinks.json".format(author_id)

        # Create a new file, or update the current file for each paper.
        with open(file_path, "w") as author_file:
           print(json.dumps(author, indent=4), file=author_file)

# Run the script given the inputs from the terminal.
main(sys.argv[1:])