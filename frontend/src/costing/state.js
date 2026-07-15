export const NUM_CONES = 5;
export const NUM_STRAKES = 8;

export function emptyCone(name = "") {
  return {
    name,
    height_select: false,
    angle_select: true,
    conic_select: 0,
    offset_select: 0,
    slope_select: 0,
    diam_large: 0,
    diam_small: 0,
    height: 0,
    angle: 0,
    offset_amt: 0,
    knuckle_rad: 0,
    sand_height: 0,
    skirt: 0,
    waste: 0,
    thick: 0,
    width: 0,
    weight_cucm: 8166,
    price_kg: 0,
    num_hours: 0,
    grade: "",
    volume_treat: 0,
  };
}

export function emptyStrake(name = "") {
  return {
    used: 0,
    name,
    num_iden_strakes: 1,
    trim_strakes: 0,
    grade: "",
    thick: 0,
    width: 0,
    weight_cucm: 8166,
    coil_length: 0,
    price_kg: 0,
    num_hours: 0,
    rate_hour: 0,
    volume_treat: 0,
  };
}

export function defaultCosting() {
  return {
    version: 1,
    title: "Untitled costing",
    customer_id: null,
    costing_id: null,
    cones_rate_per_hour: 55,
    selected_components: [],
    summary: {
      diam: 1200,
      expan_diam: 450,
      expan_height: 100,
      other_vol: 0,
      coil_mark_up_percent: 25,
      coil_misc: 0,
      floor_multi_tot: 0,
      components_price: 0,
      comp: [0, 0, 0, 0],
      comp_markup_percent: 0,
      gst: 1.1,
      num_tanks: 1,
      price_quoted: 0,
      lab_misc_hrs: 0,
      lab_misc_rate: 50,
      lab_components_hrs: 0,
      lab_components_amt: 0,
      single_add_on: [0, 0, 0],
      multi_add_on: [0, 0, 0],
    },
    cones: [
      { ...emptyCone("Top cone"), conic_select: 1, angle_select: true, angle: 10, diam_large: 1200, diam_small: 450, knuckle_rad: 30, waste: 300, thick: 2, width: 1500, price_kg: 5.8 },
      emptyCone("Top tank floor"),
      emptyCone("Bottom cone"),
      { ...emptyCone("Bottom floor"), slope_select: 1, angle_select: true, angle: 2.5, diam_large: 1200, diam_small: 50, knuckle_rad: 50, skirt: 50, thick: 1.6, width: 1200, price_kg: 4.91, volume_treat: 7 },
      emptyCone(),
    ],
    strakes: [
      { ...emptyStrake("Top strake"), used: 1, thick: 2, width: 1500, coil_length: 3769.91, price_kg: 5.8 },
      emptyStrake("Strake 2"),
      emptyStrake("Strake 3"),
      emptyStrake("Strake 4"),
      emptyStrake("Strake 5"),
      emptyStrake("Strake 6"),
      emptyStrake("Strake 7"),
      emptyStrake("Strake 8"),
    ],
    results: null,
  };
}

export function serializeCosting(state) {
  const { results, ...payload } = state;
  return JSON.stringify(payload, null, 2);
}

export function parseCosting(json) {
  const data = typeof json === "string" ? JSON.parse(json) : json;
  if (!data.summary || !data.cones || !data.strakes) {
    throw new Error("Invalid costing file: missing summary, cones, or strakes");
  }
  return { ...defaultCosting(), ...data, results: null };
}
