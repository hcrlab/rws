import {LitElement, html, css} from 'lit-element';
import {Button} from "@material/mwc-button";
import {Dialog} from "@material/mwc-dialog";
import {Drawer} from "@material/mwc-drawer"
import {TopAppBar} from "@material/mwc-top-app-bar"
import {IconButton} from "@material/mwc-icon-button"
import {List} from "@material/mwc-list"
import {ListItem} from "@material/mwc-list/mwc-list-item"
import {Icon} from "@material/mwc-icon"

class RobotWebServer extends LitElement {
    static get properties() {
        return {
            title: {type: String},
        };
    }

    constructor() {
        super();
        this.title = 'Robot Web Server';
        this.drawerOpened = false;
    }

    static get properties() {
        return {
            'name': String,
            'drawerOpened': Boolean,
        };
    }

    static get styles() {
        return [
            css`
        
      `,
        ];
    }

    clickHandler(e) {
        console.log(e.target);
        this.drawerOpened = !this.drawerOpened;
    }

    render() {
        return html`
<mwc-drawer hasHeader type="modal" ?open="${this.drawerOpened}">
    <div>
        <mwc-list activatable>
            <mwc-list-item graphic="icon" selected activated>
            <span>Home</span>
            <mwc-icon slot="graphic">home</mwc-icon>
            </mwc-list-item>
        </mwc-list>
    </div>
    <div slot="appContent">
      <mwc-top-app-bar>
        <mwc-icon-button slot="navigationIcon" icon="menu" @click="${this.clickHandler}"></mwc-icon-button>
        <div slot="title">${this.title}</div>
      </mwc-top-app-bar>

      <p>Main content</p>

    </div>
</mwc-drawer> 
    `;
    }
}

customElements.define('robot-web-server', RobotWebServer);
