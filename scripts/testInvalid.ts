import { generatePythonTask } from "../src/utils/pythonGenerator.ts";

const config = {
  schema_version: "2025.09",
  filtering: {
    enabled: true,
    value: { l_freq: 1, h_freq: 40, notch_freqs: [60], notch_widths: 4 },
  },
  invalid_section: {},
};

console.log(generatePythonTask("TestInvalid", config));
