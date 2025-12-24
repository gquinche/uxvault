import streamlit as st
import uxvault.backend.supabase_client as supabase_client
import importlib
importlib.reload(supabase_client)

# Dialog-style login UI with Material icon and friendly wording.
# Uses the runtime user API (`st.user` preferred, or `st.experimental_user`) when available.


def _render_signin_body():
    """Render the sign-in UI. This function can be used inside a dialog decorator or a plain container."""
    # Use the Streamlit material icon token format in headings and buttons (e.g. :material/login:)
    st.markdown(":material/login: **Sign in to UX Vault**")
    st.caption("Access your surveys, analyses and shared results")
    st.divider()
    with st.container( gap="medium", horizontal_alignment="center"):
    

        # Prefer runtime-provided user object
        user_obj = getattr(st, "user", None) or getattr(st, "experimental_user", None)

        if user_obj is not None:
            # Use the runtime's user object for all auth state
            try:
                if getattr(user_obj, "is_logged_in", False):
                    # Show user details and logout
                    try:
                        for key in user_obj.keys():
                            st.info(f"**{key}**")
                        # st.json(user_obj)
                    except Exception:
                        st.write({k: getattr(user_obj, k, None) for k in dir(user_obj) if not k.startswith("_")})

                    display_name = getattr(user_obj, "name", None) or getattr(user_obj, "email", None) or "User"
                    st.header(f"Welcome, {display_name}")
                    picture = getattr(user_obj, "picture", None)
                    if picture:
                        st.image(picture, width=96)
                    if st.button(":material/logout: Logout", key="logout_button",width="stretch"):
                        try:
                            st.logout()
                        except Exception:
                            st.warning("Logout not supported in this environment.")
                else:
                    # Not logged in: primary authenticate action

                    if st.button(":material/login: Authenticate with Google", key="authenticate_button",width="stretch"):
                        try:
                            st.login("google")
                        except Exception:
                            st.warning("Authentication is not available in this environment.")

                    st.caption("Or select another sign-in method below")
                    with st.expander("Other sign-in options (coming soon)"):
                        st.write("Additional providers and methods will appear here.")
                    # Explain why username/password is not offered
                    with st.expander("Why can't I login with just a username and password?"):
                        st.write(
                            "Our current technology will log you out of your user every time you close the app, making the experience unfriendly. "
                            "Until the Streamlit library provides persistent local sessions, we plan to focus on supporting external sign-in options which persist for 30 days. "
                            "Some providers (OAuth2/OpenID Connect) are easy to set up and enable a plethora of other login options."
                        )
            except Exception as e:
                st.error(f"Error accessing runtime user object: {e}")
        else:
            # Fallback when runtime doesn't expose a user API
            if st.button(":material/login: Sign in with Google", key="google_signin_fallback"):
                try:
                    st.login("google")
                except Exception:
                    st.warning("st.login is not available in this environment; runtime does not expose a user API.")

            st.info("Authentication depends on the hosting environment. If your platform exposes `st.user`, it will be used.")

with st.container(horizontal=False,horizontal_alignment='right',border=True,):
    # centered title
    st.markdown('<h1 style="text-align: center;">Log In / Sign Up</h1>', unsafe_allow_html=True)

    # Safely obtain the runtime-provided user object (if available)
    user_obj = getattr(st, "user", None) or getattr(st, "experimental_user", None)

    if user_obj and getattr(user_obj, "is_logged_in", False):
        # Try to log in with Google stub to set up Supabase session for other methods
        try:
            supabase_secrets = None
            try:
                supabase_secrets = st.secrets.get("connections", {}).get("supabase")
            except Exception:
                supabase_secrets = None
            supabase_client.get_authenticated_client(user=user_obj, secrets=supabase_secrets)
            st.success("Logged in!")
            # This sets st.session_state.supabase_session to be used by other methods
        except Exception as e:
            st.error(f"Login failed. Please contact us for help. Error: {e}")
        else:
            display_name = getattr(user_obj, "name", None) or getattr(user_obj, "email", None) or "User"
            st.write(f"Hello {display_name} you are logged in!")
        # enabled another quick log out button here
        if st.button(":material/logout: Log out"):
            try:
                st.logout()
            except Exception:
                st.warning("Logout not supported in this environment.")
    else:
        st.write("User not logged in, press the button below to log in.")
        if st.button(":material/login: Log in"):
            if hasattr(st, "dialog"):
                # st.dialog is a decorator that should be applied to a function which renders components.
                @st.dialog("sign in")
                def _signin_dialog():
                    _render_signin_body()

                # Call the dialog function to display it
                _signin_dialog()
            else:
                # Fallback: render directly in a container
                with st.container(vertical_alignment="center",horizontal_alignment="center",horizontal=True):
                    _render_signin_body()


# TODO use supabase and the sub from the google authenticator (or other Oauth2 provider) to create user profiles and store/retrieve user data securely
# maybe possibly a hash of it
