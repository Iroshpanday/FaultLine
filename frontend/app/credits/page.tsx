import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "Photo credits: Momo Mart" };

// Every photograph on the page is a licensed stand-in from Wikimedia Commons,
// shown until the shop has photographs of its own.
const CREDITS = [
  { what: "Momos around a bowl of achar (top of the page)", by: "Rabin Tuladhar", licence: "CC BY-SA 4.0", licenceUrl: "https://creativecommons.org/licenses/by-sa/4.0", page: "https://commons.wikimedia.org/wiki/File:Nepali_Momo.jpg" },
  { what: "Momos on a steamer tray (visit)", by: "Libreravi", licence: "CC BY-SA 4.0", licenceUrl: "https://creativecommons.org/licenses/by-sa/4.0", page: "https://commons.wikimedia.org/wiki/File:Homemade_Momos_Dumplings_getting_boiled.jpg" },
  { what: "Jhol momos from above (menu)", by: "PansanLepcha", licence: "CC BY-SA 4.0", licenceUrl: "https://creativecommons.org/licenses/by-sa/4.0", page: "https://commons.wikimedia.org/wiki/File:Jhol_Momo_in_Kalimpong.jpg" },
  { what: "Amali achar (menu)", by: "Ritesh Man Tamrakar", licence: "CC BY 2.0", licenceUrl: "https://creativecommons.org/licenses/by/2.0", page: "https://commons.wikimedia.org/wiki/File:Amali_Achar.jpg" },
  { what: "Folded raw momos (how our momos are made)", by: "Ravi Dwivedi", licence: "CC BY-SA 4.0", licenceUrl: "https://creativecommons.org/licenses/by-sa/4.0", page: "https://commons.wikimedia.org/wiki/File:Homemade_wheat_flour_Momos_in_North_India.jpg" },
  { what: "Steaming momos (how our momos are made)", by: "TAPAS KUMAR HALDER", licence: "CC BY-SA 4.0", licenceUrl: "https://creativecommons.org/licenses/by-sa/4.0", page: "https://commons.wikimedia.org/wiki/File:Steamed_Momos_-_KOLKATA.jpg" },
  { what: "Momos with achar on a plate (how our momos are made)", by: "Tulsi Bhagat", licence: "CC BY-SA 4.0", licenceUrl: "https://creativecommons.org/licenses/by-sa/4.0", page: "https://commons.wikimedia.org/wiki/File:A_plate_of_Momos_with_pickle_in_Kathmandu_20220223.jpg" },
  { what: "Buff momos (freezer box)", by: "Gaurav Dhwaj Khadka", licence: "CC BY-SA 4.0", licenceUrl: "https://creativecommons.org/licenses/by-sa/4.0", page: "https://commons.wikimedia.org/wiki/File:Steam_Buff_Momo.jpg" },
  { what: "Momos with two achars (party tray)", by: "Kushal Goyal", licence: "CC BY-SA 3.0", licenceUrl: "https://creativecommons.org/licenses/by-sa/3.0", page: "https://commons.wikimedia.org/wiki/File:Momo_nepal.jpg" },
  { what: "Jhol momo bowl (jhol momo kit)", by: "Shristi Kapali", licence: "CC BY-SA 4.0", licenceUrl: "https://creativecommons.org/licenses/by-sa/4.0", page: "https://commons.wikimedia.org/wiki/File:Jhol_Momo.jpg" },
];

export default function Credits() {
  return (
    <main id="top" className="credits-page">
      <section className="section" aria-labelledby="credits-h">
        <div className="wrap">
          <div className="section-head">
            <h1 id="credits-h">Photo credits</h1>
            <p>The photographs on Momo Mart come from Wikimedia Commons under these licences.</p>
          </div>
          <ul className="rows">
            {CREDITS.map((c) => (
              <li key={c.page}>
                <span className="rows__name">
                  <a className="link" href={c.page}>{c.what}</a>
                  <small>by {c.by}</small>
                </span>
                <span className="rows__value">
                  <a className="link" href={c.licenceUrl}>{c.licence}</a>
                </span>
              </li>
            ))}
          </ul>
          <p className="credits-back"><Link className="link" href="/">Back to Momo Mart</Link></p>
        </div>
      </section>
    </main>
  );
}
