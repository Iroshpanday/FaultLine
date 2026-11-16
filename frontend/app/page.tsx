import { ChatWidget, OrderHelpButton } from "./chat-widget";
import { KitScripts } from "./kit-scripts";

/*
  Momo Mart, a place page (tasteskill). Screens at 1440x900:
  hero (1) · visit (1) · statement / word-highlight (1) · menu, tall-small (1)
  · kitchen / photo-chapters (3, set by the moment) · boxes (1) · footer.closing on the brand band (1)
  Every photograph is a licensed stand-in from Wikimedia Commons (credits in the footer line).
  Hours and prices are assumed for the demo and marked data-assumed.
*/

const ORDER_MAIL = "mailto:orders@momomart.example?subject=Momo%20order";
const AREA_MAP = "https://www.openstreetmap.org/search?query=Jhamsikhel%20Lalitpur";


const img = (id: string, widths: number[]) => ({
  src: `/assets/img/photo-${id}-${widths[widths.length - 1]}.webp`,
  srcSet: widths.map((w) => `/assets/img/photo-${id}-${w}.webp ${w}w`).join(", "),
});

const Arrow = () => (
  <svg className="m-arrow" viewBox="0 0 12 12" aria-hidden="true">
    <path className="m-arrow__stem" d="M1 6h8" />
    <path className="m-arrow__head" d="M4.5 2.5 8 6l-3.5 3.5" />
  </svg>
);

const BOXES = [
  {
    id: "f80104402",
    widths: [640, 960, 1440],
    alt: "Buff momos glistening on a steel plate",
    title: "Momo freezer box",
    price: "Rs 1,250",
    facts: "50 momos, ready in ten minutes",
    text: "Chicken, buff or veg, with tomato achar.",
    subject: "Freezer%20box",
  },
  {
    id: "f20906619",
    widths: [640, 960],
    alt: "A ring of momos around bowls of yellow and dark achar",
    title: "Momo party tray",
    price: "Rs 2,400",
    facts: "100 momos, order a day ahead",
    text: "Two fillings and two achars for eight.",
    subject: "Party%20tray",
  },
  {
    id: "f86239159",
    widths: [640, 960, 1440],
    alt: "Momos in an orange sesame-tomato jhol",
    title: "Jhol momo kit",
    price: "Rs 1,450",
    facts: "30 momos and 400 ml of jhol",
    text: "Chicken momos to pour the jhol over.",
    subject: "Jhol%20momo%20kit",
  },
];

export default function Home() {
  const hero = img("f144720603", [640, 960, 1440]);
  const visit = img("f116736448", [640, 960]);
  const tall = img("f193111906", [640, 960]);
  const small = img("f22902656", [640, 960]);
  const ch1 = img("f116733843", [640, 960]);
  const ch2 = img("f80246473", [640, 960, 1440, 1920]);
  const ch3 = img("f125686379", [640, 960, 1440]);

  return (
    <>
      <header className="nav nav--split">
        <div className="wrap nav__bar">
          <a className="skip-link" href="#top">
            Skip to content
          </a>
          <nav className="nav__links" aria-label="Main">
            <div className="nav__item">
              <a className="nav__link" href="#menu">
                Menu
              </a>
            </div>
            <div className="nav__item">
              <a className="nav__link" href="#kitchen">
                Kitchen
              </a>
            </div>
            <div className="nav__item">
              <a className="nav__link" href="#boxes">
                Boxes
              </a>
            </div>
            <div className="nav__item">
              <a className="nav__link" href="#visit">
                Visit
              </a>
            </div>
          </nav>
          <a className="nav__logo" href="#top">
            <span className="mark" data-mark="petal" aria-hidden="true"></span>Momo Mart
          </a>
          <div className="nav__actions">
            <OrderHelpButton className="nav__link" />
            <a className="btn btn--primary" href={ORDER_MAIL}>
              Order momos
            </a>
          </div>
          <button className="nav__toggle" type="button" aria-expanded="false" aria-label="Menu">
            <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true">
              <path d="M2 5h14M2 13h14" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
            </svg>
          </button>
        </div>
      </header>

      <main id="top">
        <section className="hero hero--split" data-enter="" aria-labelledby="hero-h">
          <div className="wrap">
            <div className="hero-text grid hero-split">
              <div className="hero-copy span-6">
                <p className="hero-notice" data-assumed="">
                  Same-day delivery in the valley on orders before 14:00
                </p>
                <h1 id="hero-h">Momos, folded by hand in Jhamsikhel</h1>
                <p className="t-lead">
                  Eat them hot at our counter in Lalitpur or take a frozen box home.{" "}
                  <span data-assumed="">Open 7:00 to 19:00, every day.</span>
                </p>
                <div className="btn-row">
                  <a className="btn btn--primary" href={ORDER_MAIL}>
                    Order momos
                    <Arrow />
                  </a>
                  <a className="btn btn--secondary" href="#menu">
                    See the menu
                  </a>
                </div>
                <dl className="hero-facts" data-assumed="">
                  <div>
                    <dt>A plate of ten</dt>
                    <dd>from Rs 180</dd>
                  </div>
                  <div>
                    <dt>Frozen box</dt>
                    <dd>50 momos</dd>
                  </div>
                  <div>
                    <dt>Steams at home in</dt>
                    <dd>12 minutes</dd>
                  </div>
                </dl>
              </div>
              <div className="hero-visual frame frame--photo span-6 start-7">
                <img
                  className="frame__img"
                  src={hero.src}
                  srcSet={hero.srcSet}
                  sizes="(max-width: 1023px) 100vw, 50vw"
                  width={1440}
                  height={960}
                  alt="Steam rising from a bowl of freshly steamed momos"
                  style={{ objectPosition: "50% 62%" }}
                  fetchPriority="high"
                  data-source="stand-in"
                  data-subject="steamed momos"
                />
              </div>
            </div>
          </div>
        </section>

        <section className="section" id="visit" data-place="visit" aria-labelledby="visit-h">
          <div className="wrap">
            <div className="section-head">
              <h2 id="visit-h">Visit the kitchen in Jhamsikhel</h2>
            </div>
            <div className="grid grid--top">
            <div className="visit visit--card span-6">
              <div className="visit__cols">
                <div className="visit__col stack-4">
                  <address className="visit__address">
                    Jhamsikhel
                    <br />
                    Lalitpur
                  </address>
                  <a className="link" href={AREA_MAP}>
                    See the area
                  </a>
                </div>
                <div className="visit__col">
                  <dl className="hours" data-tz="Asia/Kathmandu" data-assumed="">
                    <dt>Sun to Fri</dt>
                    <dd>7:00 to 19:00</dd>
                    <dt>Sat</dt>
                    <dd>8:00 to 17:00</dd>
                  </dl>
                </div>
              </div>
              <ul className="visit__rows" data-assumed="">
                <li>
                  <span>Delivery</span>
                  <span>Kathmandu Valley, same day before 14:00</span>
                </li>
                <li>
                  <span>Pickup</span>
                  <span>Frozen boxes ready in 10 minutes</span>
                </li>
                <li>
                  <span>Questions about an order</span>
                  <OrderHelpButton className="link" label="Ask order help" />
                </li>
              </ul>
            </div>
            <figure className="pl-photo pl-photo--end span-6 start-7" style={{ ["--pl-r" as string]: "1.333" }}>
              <img
                src={visit.src}
                srcSet={visit.srcSet}
                sizes="(max-width: 1023px) 100vw, 50vw"
                width={960}
                height={1280}
                alt="Fresh momos on a steamer tray, ready for the pot"
                loading="lazy"
                data-source="stand-in"
                data-subject="momos steaming"
              />
            </figure>
            </div>
          </div>
        </section>

        <section className="section statement" id="about" data-moment="word-highlight" aria-label="The kitchen">
          <div className="wrap">
            <p className="t-label">The kitchen</p>
            <p className="mo-wh__text">
              Every momo is folded by hand on the morning it is sold, frozen within the hour, and steams at
              home in twelve minutes, the way it does at <strong>our counter</strong>.
            </p>
          </div>
        </section>

        <section className="section" id="menu" aria-labelledby="menu-h">
          <div className="wrap">
            <div className="section-head grid head-row">
              <h2 id="menu-h" className="span-6">Momos, achar and tea</h2>
              <p className="span-6 start-7">
                Plates of ten at the counter. <a className="link" href="#boxes">See the frozen boxes</a>
              </p>
            </div>
            <div className="grid grid--top menu-grid">
              <div className="span-3">
                <p className="t-label">Momos</p>
                <ul className="rows" data-assumed="">
                  <li>
                    <span className="rows__name">
                      Chicken momo<small>Ginger, garlic, coriander</small>
                    </span>
                    <span className="rows__value">Rs 220</span>
                  </li>
                  <li>
                    <span className="rows__name">
                      Buff momo<small>Spring onion and timur</small>
                    </span>
                    <span className="rows__value">Rs 240</span>
                  </li>
                  <li>
                    <span className="rows__name">
                      Veg momo<small>Cabbage, paneer, carrot</small>
                    </span>
                    <span className="rows__value">Rs 180</span>
                  </li>
                  <li>
                    <span className="rows__name">
                      Jhol momo<small>In sesame-tomato soup</small>
                    </span>
                    <span className="rows__value">Rs 260</span>
                  </li>
                  <li>
                    <span className="rows__name">
                      Kothey momo<small>Pan-fried on one side</small>
                    </span>
                    <span className="rows__value">Rs 250</span>
                  </li>
                </ul>
              </div>
              <div className="span-3">
                <p className="t-label">Achar and tea</p>
                <ul className="rows" data-assumed="">
                  <li>
                    <span className="rows__name">
                      Tomato achar<small>Roasted, with sesame, 250 g</small>
                    </span>
                    <span className="rows__value">Rs 320</span>
                  </li>
                  <li>
                    <span className="rows__name">
                      Timur chutney<small>Bright and numbing, 150 g</small>
                    </span>
                    <span className="rows__value">Rs 280</span>
                  </li>
                  <li>
                    <span className="rows__name">
                      Mula ko achar<small>Radish in mustard oil, 400 g</small>
                    </span>
                    <span className="rows__value">Rs 360</span>
                  </li>
                  <li>
                    <span className="rows__name">
                      Ilam tea<small>Second flush, 100 g</small>
                    </span>
                    <span className="rows__value">Rs 650</span>
                  </li>
                  <li>
                    <span className="rows__name">
                      Momo masala<small>Our filling spice, 100 g</small>
                    </span>
                    <span className="rows__value">Rs 220</span>
                  </li>
                </ul>
              </div>
              <figure className="pl-photo span-3 start-7 menu-photo" style={{ ["--pl-r" as string]: ".8" }}>
                <img
                  src={tall.src}
                  srcSet={tall.srcSet}
                  sizes="(max-width: 639px) 50vw, (max-width: 1023px) 100vw, 25vw"
                  width={960}
                  height={1280}
                  alt="Jhol momos in an orange soup, seen from above"
                  loading="lazy"
                  data-source="stand-in"
                  data-subject="jhol momo"
                />
              </figure>
              <figure className="pl-photo span-3 start-10 menu-photo" style={{ ["--pl-r" as string]: ".8" }}>
                <img
                  src={small.src}
                  srcSet={small.srcSet}
                  sizes="(max-width: 639px) 75vw, (max-width: 1023px) 100vw, 25vw"
                  width={960}
                  height={720}
                  alt="Glossy amali achar with whole chilies"
                  loading="lazy"
                  data-source="stand-in"
                  data-subject="achar"
                />
              </figure>
            </div>
          </div>
        </section>

        <section className="section" id="kitchen" data-moment="photo-chapters" aria-labelledby="kitchen-h">
          <div className="wrap mo-ph">
            <div className="mo-ph__head">
              <h2 id="kitchen-h">How our momos are made</h2>
              <p>Every box goes through the same three steps on the same morning.</p>
            </div>
            <ol className="mo-ph__list">
              <li className="mo-ph__ch">
                <figure className="mo-ph__pic">
                  <img
                    src={ch1.src}
                    srcSet={ch1.srcSet}
                    sizes="(max-width: 639px) 240vw, 100vw"
                    width={960}
                    height={1280}
                    alt="Rows of freshly folded raw momos on a tray"
                    style={{ objectPosition: "50% 88%" }}
                    data-source="stand-in"
                    data-subject="folded momos"
                  />
                </figure>
                <h3>Folded by hand</h3>
                <p>Twelve pleats on every momo, folded at the board from six in the morning.</p>
              </li>
              <li className="mo-ph__ch">
                <figure className="mo-ph__pic">
                  <img
                    src={ch2.src}
                    srcSet={ch2.srcSet}
                    sizes="(max-width: 639px) 240vw, 100vw"
                    width={1920}
                    height={1579}
                    alt="A ring of steamed momos around a bowl of sesame-tomato achar"
                    data-source="stand-in"
                    data-subject="steamed momos"
                  />
                </figure>
                <h3>Steamed, then frozen</h3>
                <p>A test batch goes in the steamer. The rest is in the freezer within the hour.</p>
              </li>
              <li className="mo-ph__ch">
                <figure className="mo-ph__pic">
                  <img
                    src={ch3.src}
                    srcSet={ch3.srcSet}
                    sizes="(max-width: 639px) 240vw, 100vw"
                    width={1440}
                    height={1440}
                    alt="A plate of momos with tomato achar, served at the counter"
                    data-source="stand-in"
                    data-subject="momos served"
                  />
                </figure>
                <h3>Served with achar</h3>
                <p>On a steel plate at the counter, or at home with the jar of achar from your box.</p>
              </li>
            </ol>
          </div>
        </section>

        <section className="section" id="boxes" aria-labelledby="boxes-h">
          <div className="wrap">
            <div className="section-head grid head-row">
              <h2 id="boxes-h" className="span-6">Frozen boxes to take home</h2>
              <p className="span-6 start-7">Collect at the counter or get same-day delivery in the valley.</p>
            </div>
            <div className="grid grid--top">
              {BOXES.map((b) => {
                const pic = img(b.id, b.widths);
                return (
                  <a
                    key={b.id}
                    className="tile span-4"
                    href={`mailto:orders@momomart.example?subject=${b.subject}`}
                  >
                    <div className="tile__media">
                      <img
                        src={pic.src}
                        srcSet={pic.srcSet}
                        sizes="(max-width: 1023px) 100vw, 33vw"
                        width={960}
                        height={720}
                        alt={b.alt}
                        loading="lazy"
                        data-source="stand-in"
                        data-subject={b.title}
                      />
                    </div>
                    <div className="tile__head">
                      <h3>{b.title}</h3>
                      <span className="tile__price" data-assumed="">
                        from {b.price}
                      </span>
                    </div>
                    <p className="tile__facts">{b.facts}</p>
                    <p>{b.text}</p>
                    <span className="link">
                      Order this box
                      <Arrow />
                    </span>
                  </a>
                );
              })}
            </div>
          </div>
        </section>
      </main>

      <footer className="footer closing ground-brand" id="contact" aria-labelledby="close-h">
        <div className="wrap">
          <div className="closing__cta close--word">
            <div className="section-head--split">
              <div>
                <h2 id="close-h">Order momos</h2>
                <p className="t-lead">Write to us and we reply within the hour while the kitchen is open.</p>
              </div>
              <a className="btn btn--primary" href={ORDER_MAIL}>
                Order momos
                <Arrow />
              </a>
            </div>
            <p className="close__word" aria-hidden="true">
              Momo Mart
            </p>
          </div>
          <div className="closing__links">
            <div className="grid">
              <div className="span-4 stack-4">
                <a className="nav__logo" href="#top">
                  <span className="mark" data-mark="petal" aria-hidden="true"></span>Momo Mart
                </a>
                <p className="footer__lede">Momos, folded by hand in Lalitpur.</p>
              </div>
              <div className="span-2 footer__col">
                <h3>Menu</h3>
                <ul>
                  <li>
                    <a href="#menu">Momos</a>
                  </li>
                  <li>
                    <a href="#menu">Achar and tea</a>
                  </li>
                </ul>
              </div>
              <div className="span-2 footer__col">
                <h3>Kitchen</h3>
                <ul>
                  <li>
                    <a href="#kitchen">How we make them</a>
                  </li>
                  <li>
                    <a href="#about">The kitchen</a>
                  </li>
                </ul>
              </div>
              <div className="span-2 footer__col">
                <h3>Boxes</h3>
                <ul>
                  <li>
                    <a href="#boxes">Frozen boxes</a>
                  </li>
                  <li>
                    <a href="#boxes">Party trays</a>
                  </li>
                </ul>
              </div>
              <div className="span-2 footer__col">
                <h3>Visit</h3>
                <ul>
                  <li>
                    <a href="#visit">Hours and area</a>
                  </li>
                  <li>
                    <a href={AREA_MAP}>See the area</a>
                  </li>
                </ul>
              </div>
            </div>
            <div className="footer__legal">
              <span>&copy; 2026 Momo Mart, a demo store for Faultline</span>
              <a className="credits" href="/credits">Photographs via Wikimedia Commons</a>
            </div>
          </div>
        </div>
      </footer>

      <nav className="actionbar" aria-label="Quick actions">
        <OrderHelpButton className="btn btn--secondary" />
        <a className="btn btn--primary" href={ORDER_MAIL}>
          Order momos
        </a>
      </nav>

      <ChatWidget />
      <KitScripts />
    </>
  );
}
