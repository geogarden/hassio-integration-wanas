const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { parseHTML } = require('linkedom');

function setup(options = {}) {
  const { window } = parseHTML('<html><body></body></html>');
  const registry = {};
  const states = {};
  const add = (domain, key, state, attributes = {}) => {
    const entity_id = `${domain}.renamed_${key}`;
    registry[entity_id] = { entity_id, translation_key: key, platform: 'wanas_community', device_id: 'wanas-device' };
    states[entity_id] = { state: String(state), attributes };
    return entity_id;
  };
  for (const [key, state] of Object.entries({ supply_airflow:138, exhaust_airflow:146, supply_fan_speed:1,
    outdoor_temperature:9.7, exhaust_temperature:11.5, supply_temperature:22.6, indoor_temperature:22.7,
    current_temperature:18.5, heat_recovery_power:600, heat_recovery_efficiency:99, filter_replacement:30 })) add('sensor', key, state);
  add('sensor','current_period',3,{ from:'05:15', until:'20:00', speed:1, temperature:22 });
  add('switch','bypass','off'); add('binary_sensor','bypass_state','off');
  add('switch','humidifier','on'); add('switch','fireplace_switch','off');
  add('number','fireplace',0);
  const calls=[];
  const hass = { entities:registry, states, language:'pl', devices:{'wanas-device':{config_entries:['entry-1']}},
    callService: async (...args) => { calls.push(args); return {response:{}}; }, callWS:async()=>({change:4.7}) };
  const context = vm.createContext({ window, document:window.document, HTMLElement:window.HTMLElement,
    customElements:window.customElements, CustomEvent:window.CustomEvent, console:{info(){}},
    IntersectionObserver:class{observe(){} disconnect(){}},
    setInterval:()=>1, clearInterval(){}, setTimeout, clearTimeout, performance, Date });
  vm.runInContext(fs.readFileSync('custom_components/wanas_community/www/wanas-cards.js','utf8'),context);
  vm.runInContext('defineCards()',context);
  const card=window.document.createElement('wanas-card'); card.setConfig(options); card.hass=hass;
  return { card, hass, calls, root:card.shadowRoot, window };
}

test('overview uses live temperatures and centers efficiency and its caption on the exchanger', () => {
  const {root}=setup();
  assert.equal(root.getElementById('tExtra').textContent,'18,5°');
  assert.equal(root.getElementById('tS').textContent,'22,6°');
  assert.equal(root.getElementById('eff').textContent,'99%');
  const box=root.querySelector('.core');
  const center=+box.getAttribute('x')+(+box.getAttribute('width'))/2;
  for(const id of ['eff','effP']) {
    assert.equal(+root.getElementById(id).getAttribute('x'),center);
    assert.equal(root.getElementById(id).getAttribute('text-anchor'),'middle');
  }
  assert.equal(root.getElementById('effP').textContent,'Sprawność odzysku');
});

test('module summary opens functions without writing; actual module control uses the existing entity', () => {
  const {root,calls}=setup();
  root.getElementById('modsSummary').firstElementChild.click();
  assert.equal(root.getElementById('panel-functions').hidden,false);
  assert.equal(root.getElementById('panel-overview').hidden,true);
  assert.equal(calls.length,0);
  root.getElementById('mods').firstElementChild.click();
  assert.deepEqual(calls[0].slice(0,2),['switch','toggle']);
  assert.equal(calls[0][2].entity_id,'switch.renamed_bypass');
});

test('schedule loads lazily for the selected device, does not write and preserves unsaved edits on state updates', async () => {
  const {card,root,calls,hass}=setup();
  assert.equal(root.querySelector('wanas-schedule-card'),null);
  root.getElementById('tab-schedule').click();
  const schedule=root.querySelector('wanas-schedule-card');
  assert.equal(schedule._config.device_id,'wanas-device');
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(calls[0][0],'wanas_community'); assert.equal(calls[0][1],'get_schedule');
  assert.equal(calls[0][2].config_entry_id,'entry-1');
  schedule._msg='unsaved';
  card.hass={...hass,states:{...hass.states,'sensor.renamed_supply_temperature':{state:'23.1',attributes:{}}}};
  assert.equal(root.querySelector('wanas-schedule-card'),schedule);
  assert.equal(schedule._msg,'unsaved'); assert.equal(calls.length,1);
  assert.equal(root.getElementById('tS').textContent,'23,1°');
  assert.equal(root.getElementById('panel-schedule').hidden,false);
});

test('timed function retains its real service and an unavailable module is disabled', () => {
  const {root,calls,card,hass}=setup();
  root.getElementById('timed').firstElementChild.click();
  assert.equal(calls[0][1],'turn_on');
  assert.equal(calls[0][2].entity_id,'switch.renamed_fireplace_switch');
  card.hass={...hass,states:{...hass.states,'switch.renamed_bypass':{state:'unavailable',attributes:{}}}};
  assert.equal(root.getElementById('mods').firstElementChild.disabled,true);
});

test('hidden sections and compact configuration remain supported', () => {
  const {root}=setup({show_modules:false,show_timed:false,show_now:false,show_diagram:false});
  assert.equal(root.querySelector('[role="tablist"]'),null);
  assert.equal(root.getElementById('tO'),null);
  const compact=setup({compact:true});
  assert.equal(compact.root.querySelector('[role="tablist"]'),null);
  assert.equal(compact.root.getElementById('g').textContent,'I');
});

test('zero and missing temperatures, unavailable efficiency and bypass do not show sample values', () => {
  const {card,hass,root}=setup();
  card.hass={...hass,states:{...hass.states,'sensor.renamed_current_temperature':{state:'0',attributes:{}},
    'sensor.renamed_heat_recovery_efficiency':{state:'unavailable',attributes:{}}}};
  assert.equal(root.getElementById('tExtra').textContent,'0,0°');
  assert.equal(root.getElementById('eff').textContent,'—');
  card.hass={...hass,states:{...hass.states,'sensor.renamed_current_temperature':{state:'unavailable',attributes:{}},
    'switch.renamed_bypass':{state:'on',attributes:{}}}};
  assert.equal(root.getElementById('tExtra').textContent,'—');
  assert.equal(root.getElementById('eff').textContent,'bypass');
});
