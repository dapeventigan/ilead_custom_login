/* @odoo-module */

import { Component, useState, onWillStart } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { session } from "@web/session";

import { _t } from "@web/core/l10n/translation";

class IleadSystray extends Component {
  static template = "ilead_auto_logout.IleadSystray";
  setup() {
    this.state = useState({
      ilead_idle_time: null,
    });

    onWillStart(async () => {
      var self = this;
      var now = new Date().getTime();
      rpc("/get_idle_time/timer", {}).then((data) => {
        if (data) {
          self.minutes = data;
          self.idle_timer();
        }
      });
    });
  }

  idle_timer() {
    var self = this;
    var nowt = new Date().getTime();
    var date = new Date(nowt);
    date.setMinutes(date.getMinutes() + self.minutes);
    var updatedTimestamp = date.getTime();

    var idle = setInterval(function () {
      var now = new Date().getTime();
      var distance = updatedTimestamp - now;
      var days = Math.floor(distance / (1000 * 60 * 60 * 24));
      var hours = Math.floor(
        (distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60),
      );
      var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      var seconds = Math.floor((distance % (1000 * 60)) / 1000);
      if (hours && days) {
        self.state.ilead_idle_time =
          days + "d " + hours + "h " + minutes + "m " + seconds + "s ";
      } else if (hours) {
        self.state.ilead_idle_time =
          hours + "h " + minutes + "m " + seconds + "s ";
      } else {
        self.state.ilead_idle_time = minutes + "m " + seconds + "s ";
      }

      if (distance < 0) {
        clearInterval(idle);
        self.state.ilead_idle_time = "Session Expired";
        location.replace("/web/session/logout");
      }
    }, 1000);

    document.onmousemove = () => {
      var nowt = new Date().getTime();
      var date = new Date(nowt);
      date.setMinutes(date.getMinutes() + self.minutes);
      updatedTimestamp = date.getTime();
    };

    document.onkeypress = () => {
      var nowt = new Date().getTime();
      var date = new Date(nowt);
      date.setMinutes(date.getMinutes() + self.minutes);
      updatedTimestamp = date.getTime();
    };

    document.onclick = () => {
      var nowt = new Date().getTime();
      var date = new Date(nowt);
      date.setMinutes(date.getMinutes() + self.minutes);
      updatedTimestamp = date.getTime();
    };

    document.ontouchstart = () => {
      var nowt = new Date().getTime();
      var date = new Date(nowt);
      date.setMinutes(date.getMinutes() + self.minutes);
      updatedTimestamp = date.getTime();
    };

    document.onmousedown = () => {
      var nowt = new Date().getTime();
      var date = new Date(nowt);
      date.setMinutes(date.getMinutes() + self.minutes);
      updatedTimestamp = date.getTime();
    };

    document.onload = () => {
      var nowt = new Date().getTime();
      var date = new Date(nowt);
      date.setMinutes(date.getMinutes() + self.minutes);
      updatedTimestamp = date.getTime();
    };
  }
}
export const systrayItem = {
  Component: IleadSystray,
};
registry
  .category("systray")
  .add("ilead_auto_logout.IleadSystray", systrayItem, {
    sequence: 25,
  });
