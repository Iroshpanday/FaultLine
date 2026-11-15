// Demo catalog. Static on purpose: products aren't part of the backend yet.
export type Product = {
  id: string;
  name: string;
  description: string;
  size: string;
  price: number; // NPR
  tag?: string;
};

export type Section = { id: string; title: string; intro: string; products: Product[] };

export const SECTIONS: Section[] = [
  {
    id: "momos",
    title: "Frozen momos",
    intro: "Folded by hand each morning and frozen within the hour. Steam from frozen in 12 minutes.",
    products: [
      {
        id: "chicken",
        name: "Chicken momo",
        description: "Minced thigh with ginger, garlic and fresh coriander. Juicy, not greasy.",
        size: "50 pieces",
        price: 1250,
        tag: "Most ordered",
      },
      {
        id: "buff",
        name: "Buff momo",
        description: "The Kathmandu classic: buffalo, spring onion and a little timur.",
        size: "50 pieces",
        price: 1350,
      },
      {
        id: "veg",
        name: "Veg momo",
        description: "Cabbage, paneer and carrot with a pinch of cumin.",
        size: "50 pieces",
        price: 950,
      },
      {
        id: "jhol-kit",
        name: "Jhol momo kit",
        description: "30 chicken momos with a pot of sesame-tomato jhol to pour over.",
        size: "30 pieces + 400 ml",
        price: 1450,
        tag: "New",
      },
    ],
  },
  {
    id: "achar",
    title: "Achar and chutney",
    intro: "Made in small batches in Bhaktapur. Every jar is dated.",
    products: [
      {
        id: "tomato-achar",
        name: "Tomato and sesame achar",
        description: "Roasted tomato, toasted sesame and chili. The one momos are made for.",
        size: "250 g jar",
        price: 320,
      },
      {
        id: "timur-chutney",
        name: "Timur chutney",
        description: "Bright and numbing. A spoonful wakes up any plate.",
        size: "150 g jar",
        price: 280,
      },
      {
        id: "mula-achar",
        name: "Mula ko achar",
        description: "Sun-dried radish in mustard oil, fermented for three weeks.",
        size: "400 g jar",
        price: 360,
      },
    ],
  },
  {
    id: "tea",
    title: "Tea and spices",
    intro: "For the cup after the plate.",
    products: [
      {
        id: "ilam-tea",
        name: "Ilam orthodox tea",
        description: "Second flush, whole leaf. Light, floral and good without milk.",
        size: "100 g",
        price: 650,
      },
      {
        id: "momo-masala",
        name: "Momo masala",
        description: "Our filling spice blend, for when you fold your own.",
        size: "100 g",
        price: 220,
      },
      {
        id: "timur",
        name: "Whole timur",
        description: "Himalayan Sichuan pepper. Crush just before using.",
        size: "50 g",
        price: 300,
      },
    ],
  },
];

export const formatPrice = (npr: number) => `Rs ${npr.toLocaleString("en-IN")}`;
